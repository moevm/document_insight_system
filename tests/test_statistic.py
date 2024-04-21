import time
from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

class StatisticTestSelenium(BasicSeleniumTest):

    def test_open_statistic(self):
        self.authorization()
        URL = self.get_url('/check_list')
        self.get_driver().get(URL)
        self.get_driver().implicitly_wait(30)
        try:
            string_in_table = self.driver.find_element(By.XPATH, "//table[@id='check-list-table']//tr/td/a")
            self.assertNotEqual(string_in_table, None)
        except NoSuchElementException:
            empty_table = self.driver.find_element(By.CLASS_NAME, "no-records-found")
            self.assertNotEqual(empty_table, None)
