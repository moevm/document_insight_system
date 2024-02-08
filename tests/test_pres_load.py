import os
from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By

class PresLoadTestSelenium(BasicSeleniumTest):

    def test_pres_load(self):
        self.authorization()
        URL = self.getUrl('/check_list')
        self.getDriver().get(URL)
        self.getDriver().implicitly_wait(30)
        obj = self.getDriver().find_element(By.CLASS_NAME, "fixed-table-container")
        self.assertNotEquals(obj, None)
    
