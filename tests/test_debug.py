import os
from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By

class DebugTestSelenium(BasicSeleniumTest):

    def test_open_statistic(self):
        host, login_param, password_param = self.param
        URL = self.getUrl('/login')
        self.getDriver().get(URL)
        self.getDriver().implicitly_wait(30)
        login = self.getDriver().find_element(By.ID, "login_text_field")
        login.clear()
        login.send_keys(login_param)
        password = self.getDriver().find_element(By.ID, "password_text_field")
        password.clear()
        password.send_keys(password_param)
        login_button = self.getDriver().find_element(By.ID, "login_button")
        login_button.click()
        URL = self.getUrl('/check_list')
        self.getDriver().get(URL)
        self.getDriver().implicitly_wait(30)
        obj = self.getDriver().find_element(By.CLASS_NAME, "fixed-table-container")
        self.assertNotEquals(obj, None)
    
