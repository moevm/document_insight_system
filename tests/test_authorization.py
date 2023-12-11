import unittest
import time
from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By

# AUTH_URL = 'https://slides-checker.moevm.info/login'

class AuthTestSelenium(BasicSeleniumTest):

    def test_loading(self):
        URL = self.getUrl('/login')
        self.getDriver().get(URL)
        self.getDriver().implicitly_wait(30)
        obj = self.getDriver().find_element(By.CLASS_NAME, "form-group")
        self.assertNotEquals(obj, None)
        return True


    def failed_auth(self):
        URL = self.getUrl('/login')
        self.getDriver().get(URL)
        self.getDriver().implicitly_wait(30)

        login = self.getDriver().find_element(By.ID, "login_text_field")
        login.clear()
        login.send_keys('wrong_login')

        password = self.getDriver().find_element(By.ID, "password_text_field")
        password.clear()
        password.send_keys('wrong_password')

        login_button = self.getDriver().find_element(By.ID, "login_button")
        login_button.click()
        obj = self.getDriver().find_element(By.CLASS_NAME, "invalid-feedback ins")
        self.assertNotEquals(obj, None)

