from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By


class AdminCriterionsTestSelenium(BasicSeleniumTest):
    def begin(self):
        self.authorization()
        URL = self.get_url('/admin')
        self.get_driver().get(URL)
        self.get_driver().implicitly_wait(30)
        page_text = self.driver.find_element(By.TAG_NAME, "body").text
        if 'администратор' not in page_text.lower():
            self.skipTest("This test runs inly with admin's login and password")
        else:
            URL = self.get_url('/admin/criterions')
            self.get_driver().get(URL)
            self.get_driver().implicitly_wait(30)

    def test_open_criterions_list(self):
        self.begin()
        table = self.driver.find_element(By.ID, 'results_table')
        self.assertNotEqual(table, None)
        rows = table.find_elements(By.TAG_NAME, 'tr')
        self.assertNotEqual(rows, None)
        headers = self.driver.find_elements(By.XPATH, "//table//th")
        header_id = any("id" in header.text.lower() for header in headers)
        header_label = any('label' in header.text.lower() for header in headers)
        self.assertTrue(header_id, 'Id header is not found')
        self.assertTrue(header_label, 'label header is not found')

    def test_open_description(self):
        self.begin()
        button = self.driver.find_element(
            By.CSS_SELECTOR, '#results_table tbody tr[data-index="0"] a.detail-icon'
        )
        button.click()
        description = self.driver.find_element(
            By.CSS_SELECTOR, '#results_table tbody tr.detail-view td'
        ).text.strip()
        self.assertTrue(description, 'Criterion description is empty')
