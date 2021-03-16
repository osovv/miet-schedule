from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from Lesson import Lesson


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
        self.table_body = None
        self.table_header = None
        self.semester = None
        self.semester_title = None
        self.week_name = None
        self.week_type = None
        self.days_names = None
        self.days_types = None
        self.schedule_type = None
        self.group_name = None
        self.lesson_entries = None
        self.cell_text = None
        self.times = None
        self.days_schedule = {
            'Понедельник': [],
            'Вторник': [],
            'Среда': [],
            'Четверг': [],
            'Пятница': [],
            'Суббота': [],
        }

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
        else:
            self.group_name = group_name
        return status

    def get_session_id(self) -> int:
        self.click_dropdown_menu()
        ids = self.driver.find_elements_by_xpath('//*[@id]')
        return ids[-1].get_attribute('id')

    def click_button(self, xpath: str) -> bool:
        try:
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
            return True
        except NoSuchElementException:
            print(f"Couldn't find button with xpath = {xpath}")
            return False

    def get_table(self, period: str = 'today') -> bool:
        if self.group_chosen:
            self.click_dropdown_menu()
            if period == 'today':
                self.choose_day_schedule()
                self.schedule_type = 'today'
            if period == 'week':
                self.choose_week_schedule()
                self.schedule_type = 'week'
            soup = BeautifulSoup(self.driver.page_source, "lxml")
            schedule = soup.find(class_='schedule')
            tabs = schedule.find_all('tr')
            if tabs:
                self.table_header = schedule.find('thead')
                self.table_body = schedule.find('tbody')
                self.semester = soup.find(class_='semestr')
                return True
            return False
        else:
            print('Must choose group before getting table.')
            return False

    def parse_semester(self) -> None:
        if self.semester is not None:
            self.semester_title, self.week_name = self.semester.text.split('.')
            if self.week_name.startswith('1-й ч'):
                self.week_type = 0
            elif self.week_name.startswith('1-й з'):
                self.week_type = 1
            elif self.week_name.startswith('2-й ч'):
                self.week_type = 2
            elif self.week_name.startswith('2-й з'):
                self.week_type = 3
            self.semester_title = self.semester_title[:-2]

    def parse_table_header(self) -> None:
        if self.table_header is not None:
            if self.schedule_type == 'today':
                self.days_names = []
                for th in self.table_header.find_all('th', class_='day'):
                    # print(th.text)
                    # print(th.text.split(' '))
                    th_date, th_day_name = th.text.split(' ')
                    th_day_name = th_day_name[1:-1]
                    self.days_names.append((th_day_name, th_date))
            elif self.schedule_type == 'week':
                self.days_names = [
                    ('Понедельник',),
                    ('Вторник',),
                    ('Среда',),
                    ('Четверг',),
                    ('Пятница',),
                    ('Суббота',),
                ]

    def parse_table_body(self) -> None:
        tr_tags = []
        self.cell_text = []
        self.times = []
        for tr in self.table_body.find_all('tr'):
            tr_tags.append(tr)
            div_cell = tr.find('div', class_='cell')
            self.cell_text.append(div_cell.text)
            div_time = tr.find('th', class_='time').find('div')
            div_time = str(div_time).replace('<div>', '').replace('<hr/>', '|').replace('<br/>', '|').replace(
                '</div>', '|')
            div_items = div_time.split('|')
            if len(div_items) == 6:
                del div_items[3:5]
            self.times.append(div_time)
            classroom = ''
            title = ''
            if div_cell.text != '':
                classroom = div_cell.text.split(' | ')[0]
                title = div_cell.text.split(' | ')[1]
            self.days_schedule[self.days_names[0][0]].append(
                Lesson(
                    number=int(div_items[0][0]),
                    start_time=div_items[1],
                    end_time=div_items[2],
                    classroom=classroom,
                    title=title
                )
            )

    def form_report(self) -> str:
        schedule_string = ''
        for i in range(7):
            schedule_string = '{}\n{}'.format(schedule_string, self.days_schedule[self.days_names[0][0]][i])
        report = '{}\n{}, {}\n{}\n\nГруппа: {}\n{}'.format(
            self.semester_title,
            self.days_names[0][0],
            self.days_names[0][1],
            self.week_name,
            self.group_name,
            schedule_string
        )
        return report


if __name__ == '__main__':
    parser = Parser()
    parser.choose_group('ПИН-11')
    parser.get_table('today')
    # print(parser.table_body.prettify())
    parser.parse_semester()
    parser.parse_table_header()
    parser.parse_table_body()
    to_print = parser.form_report()
    print()
    print(to_print)
