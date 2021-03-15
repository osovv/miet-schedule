import time

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class Parser:
    def __init__(self, url: str = 'https://miet.ru/schedule'):
        self.firefox_options = webdriver.FirefoxOptions()
        self.firefox_options.headless = True
        self.driver = webdriver.Firefox(
            options=self.firefox_options,
            service_log_path='./log/geckodriver.log'
        )
        self.url = url
        self.driver.get(url)
        self.session_id = self.get_session_id()
        self.groups_names = self.get_groups_names()
        self.group_chosen = False
        self.table_content = None
        self.table_header = None

    def __del__(self):
        self.driver.close()

    def get_group_id(self, group_name: str) -> int:
        if group_name in self.groups_names:
            return self.groups_names.index(group_name) + 1
        else:
            return -1

    def get_groups_names(self) -> tuple:
        src = self.driver.page_source
        soup = BeautifulSoup(src, "lxml")
        groups = soup.find(class_='group')
        return tuple([i.string for i in groups.find_all('option') if i.string is not None])

    def choose_week_schedule(self, xpath: str = '/html/body/main/div[2]/div[2]/div[1]/div[2]/span[1]') -> bool:
        return self.click_button(xpath)

    def choose_day_schedule(self, xpath: str = '/html/body/main/div[2]/div[2]/div[1]/div[2]/span[2]') -> bool:
        return self.click_button(xpath)

    def click_dropdown_menu(self, xpath: str = '/html/body/main/div[2]/div[2]/div[1]/div[1]/span') -> bool:
        return self.click_button(xpath)

    def choose_group(self, group_name) -> bool:
        group_id = self.get_group_id(group_name)
        if group_id == -1:
            print(f"Couldn't find group {group_name}")
            return False
        xpath = f"//*[@id='{self.session_id}']/li[{group_id}]"
        status = self.click_button(xpath)
        self.group_chosen = status
        if not status:
            print(f"Could find group {group_name} with group_id = {group_id}")
        return status

    def get_session_id(self) -> int:
        self.click_dropdown_menu()
        ids = self.driver.find_elements_by_xpath('//*[@id]')
        return ids[-1].get_attribute('id')

    def click_button(self, xpath: str) -> bool:
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
            return True
        except NoSuchElementException:
            print(f"Couldn't find button with xpath = {xpath}")

    def get_table(self) -> bool:
        if self.group_chosen:
            self.click_dropdown_menu()
            self.choose_day_schedule()
            soup = BeautifulSoup(self.driver.page_source, "lxml")
            schedule = soup.find(class_='schedule')
            tabs = schedule.find_all('tr')
            if tabs:
                self.table_header, self.table_content = schedule.find_all('thead'), schedule.find_all('tbody')
                return True
            return False
        else:
            print('Must choose group before getting table.')
            return False


if __name__ == '__main__':
    parser = Parser()
    parser.get_table()
    print(parser.groups_names)
    parser.choose_group('ПИН-21')
    parser.choose_day_schedule()
    parser.get_table()
    print(parser.table_header)
    print(parser.table_content)
