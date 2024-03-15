import os
import time
from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By

class SingleCheckTestSelenium(BasicSeleniumTest):

    def test_open_check_card(self):
        self.authorization()
        URL = self.get_url('/check_list')
        self.get_driver().get(URL)
        self.get_driver().implicitly_wait(240)
        single_check = self.get_driver().find_element(By.XPATH, "//table[@id='check-list-table']//tr/td/a")
        id_check_button = single_check.get_attribute("href").split("/")[-1]
        URL = self.get_url(f'/results/{id_check_button}')
        self.get_driver().get(URL)
        obj = self.get_driver().find_element(By.ID, 'results_holder')
        self.assertNotEquals(obj, None)
    
