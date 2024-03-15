import os
import time
from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class VersionTestSelenium(BasicSeleniumTest):

    def test_version(self):
        self.authorization()    
        URL = self.get_url('/version')
        self.get_driver().get(URL)
        self.get_driver().implicitly_wait(30)
        obj = self.get_driver().find_element(By.ID, "version-table")
        self.assertNotEquals(obj, None)
    
