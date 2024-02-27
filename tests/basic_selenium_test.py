import unittest
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

class BasicSeleniumTest(unittest.TestCase):

    chrome_options = Options()
    service = Service(executable_path='/usr/bin/chromedriver')
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options=chrome_options, service=service)

    def authorization(self):
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


    def __init__(self, methodName='runTest', param=None):
        super(BasicSeleniumTest, self).__init__(methodName)
        self.param = param

    @staticmethod
    def parametrize(testcase_class, param=None):
        testloader = unittest.TestLoader()
        testnames = testloader.getTestCaseNames(testcase_class)
        suite = unittest.TestSuite()
        for name in testnames:
            suite.addTest(testcase_class(name, param=param))
        return suite

    def getUrl(self, relativePath):
        return self.param[0] + relativePath

    def getDriver(_):
        return BasicSeleniumTest.driver

    @classmethod
    def closeDriver(cls):
        cls.driver.close()
