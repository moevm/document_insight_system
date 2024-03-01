import os
import time
from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By

class VersionTestSelenium(BasicSeleniumTest):

    def test_version(self):
        self.authorization()
        time.sleep(30)
        URL = self.getUrl('/version')
        self.getDriver().get(URL)
        self.getDriver().implicitly_wait(30)
        obj = self.getDriver().find_element(By.ID, "version-table")
        self.assertNotEquals(obj, None)
    
