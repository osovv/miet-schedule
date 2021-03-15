from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

url = 'https://miet.ru/schedule'
firefox_options = webdriver.FirefoxOptions()
firefox_options.headless = True
with webdriver.Firefox(options=firefox_options, service_log_path='./log/geckodriver.log') as driver:
    driver.get(url)
    src = driver.page_source
    soup = BeautifulSoup(src, "lxml")
    groups = soup.find(class_='group')
    group_names = tuple([i.string for i in groups.find_all('option') if i.string is not None])
    print(group_names)
