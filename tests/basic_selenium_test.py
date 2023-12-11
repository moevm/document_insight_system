import unittest
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options

class BasicSeleniumTest(unittest.TestCase):
    
    # options = Options()
    # options.binary_location = r'~/home/snap/bin/firefox'
    # driver = webdriver.Firefox(options=options)

    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

    def __init__(self, methodName='runTest', param=None):
        super(BasicSeleniumTest, self).__init__(methodName)
        self.param = param

    @staticmethod
    def parametrize(testcase_klass, param=None):
        testloader = unittest.TestLoader()
        testnames = testloader.getTestCaseNames(testcase_klass)
        suite = unittest.TestSuite()
        for name in testnames:
            suite.addTest(testcase_klass(name, param=param))
        return suite

    def getUrl(self, relativePath):
        return self.param + relativePath

    def getDriver(_):
        return BasicSeleniumTest.driver

    @classmethod
    def closeDriver(cls):
        cls.driver.close()



#    def setUp(self):
#        self.driver = webdriver.Firefox()  # Chrome()

#    def tearDown(self):
#        self.driver.close()
