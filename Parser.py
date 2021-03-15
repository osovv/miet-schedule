import time

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def get_group_id(group_name, group_names):
    if group_name in group_names:
        return group_names.index(group_name) + 1
    else:
        return None


if __name__ == '__main__':
    url = 'https://miet.ru/schedule'
    dropdown_button_xpath = '/html/body/main/div[2]/div[2]/div[1]/div[1]/span'
    day_schedule_button_xpath = '/html/body/main/div[2]/div[2]/div[1]/div[2]/span[2]'
    group_name = 'ПИН-11'
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.headless = True
    with webdriver.Firefox(options=firefox_options, service_log_path='./log/geckodriver.log') as driver:
        driver.get(url)
        src = driver.page_source
        soup = BeautifulSoup(src, "lxml")
        groups = soup.find(class_='group')
        group_names = tuple([i.string for i in groups.find_all('option') if i.string is not None])
        dropdown_button = driver.find_element_by_xpath(dropdown_button_xpath)
        day_button = driver.find_element_by_xpath(day_schedule_button_xpath)
        day_button.click()
        dropdown_button.click()
        ids = driver.find_elements_by_xpath('//*[@id]')
        result_id = ids[-1].get_attribute('id')
        group_id = get_group_id(group_name, group_names)
        driver.find_element_by_xpath(f"//*[@id='{result_id}']/li[{group_id}]").click()
        WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, day_schedule_button_xpath))).click()
        dropdown_button.click()
        soup = BeautifulSoup(driver.page_source, "lxml")
        schedule = soup.find(class_='schedule')
        print(schedule)
