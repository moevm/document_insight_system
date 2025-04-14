import os
import time
from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By

class AuthTestSelenium(BasicSeleniumTest):

    def check_auth(self, login_param, password_param):
        URL = self.get_url('/login')
        self.get_driver().get(URL)
        self.get_driver().implicitly_wait(30)
        login = self.get_driver().find_element(By.ID, "login_text_field")
        login.clear()
        login.send_keys(login_param)
        password = self.get_driver().find_element(By.ID, "password_text_field")
        password.clear()
        password.send_keys(password_param)
        login_button = self.get_driver().find_element(By.ID, "login_button")
        login_button.click()

    def test_loading(self):
        URL = self.get_url('/login')
        self.get_driver().get(URL)
        self.get_driver().implicitly_wait(30)
        obj = self.get_driver().find_element(By.CLASS_NAME, "form-group")
        self.assertNotEquals(obj, None)    

    def test_failed_auth(self):
        host, login, password = self.param[:3]
        self.check_auth('wrong_login', 'wrong_password')
        obj = self.get_driver().find_element(By.ID, "login_button")
        self.assertNotEquals(obj, None)

    def test_complete_auth(self):
        host, login, password = self.param[:3]
        time.sleep(10)
        self.check_auth(login, password)
        time.sleep(10)
        upload_url = self.get_url('/upload/')
        self.assertIn(upload_url, self.get_driver().current_url)
