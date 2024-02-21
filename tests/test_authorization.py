import os
from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By

class AuthTestSelenium(BasicSeleniumTest):

    def check_auth(self, login_param, password_param):
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

    def test_loading(self):
        URL = self.getUrl('/login')
        self.getDriver().get(URL)
        self.getDriver().implicitly_wait(30)
        obj = self.getDriver().find_element(By.CLASS_NAME, "form-group")
        self.assertNotEquals(obj, None)    

    def test_failed_auth(self):
        host, login, password = self.param
        self.check_auth('wrong_login', 'wrong_password')
        obj = self.getDriver().find_element(By.ID, "login_button")
        self.assertNotEquals(obj, None)

    def test_complete_auth(self):
        host, login, password = self.param
        self.check_auth(login, password)
        upload_url = self.getUrl('/upload')
        self.assertIn(upload_url, self.getDriver().current_url)
