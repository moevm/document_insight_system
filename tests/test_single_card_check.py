import os
import time
from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By

class SingleCheckTestSelenium(BasicSeleniumTest):

    def test_open_check_card(self):
        self.authorization()
        URL = self.getUrl('/check_list')
        self.getDriver().get(URL)
        self.getDriver().implicitly_wait(240)
        single_check = self.getDriver().find_element(By.XPATH, "//table[@id='check-list-table']//tr/td/a")
        id_check_button = single_check.get_attribute("href").split("/")[-1]
        URL = self.getUrl(f'/results/{id_check_button}')
        self.getDriver().get(URL)
        obj = self.getDriver().find_element(By.ID, 'results_holder')
        self.assertNotEquals(obj, None)
    
