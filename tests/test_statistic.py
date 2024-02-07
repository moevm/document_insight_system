import os
from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By

class StatisticTestSelenium(BasicSeleniumTest):

    def test_open_statistic(self):
        self.authorization()
        URL = self.getUrl('/check_list')
        self.getDriver().get(URL)
        self.getDriver().implicitly_wait(30)
        obj = self.getDriver().find_element(By.CLASS_NAME, "fixed-table-container")
        self.assertNotEquals(obj, None)
    
