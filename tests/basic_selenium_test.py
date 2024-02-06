import unittest
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager #pip install webdriver-manager

class BasicSeleniumTest(unittest.TestCase):

    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install())) #you should have Firefox, installed not from snap
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
