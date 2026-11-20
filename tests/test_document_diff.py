from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class DocumentDiffTestSelenium(BasicSeleniumTest):
    def begin(self):
        self.authorization()
        url = self.get_url('/document_diff/')
        self.get_driver().get(url)
        self.get_driver().implicitly_wait(30)
        page_text = self.get_driver().find_element(By.TAG_NAME, 'body').text.lower()
        if 'forbidden' in page_text:
            self.skipTest('Document comparison is available only to administrators')

    def test_open_document_diff_page(self):
        self.begin()

        form = self.get_driver().find_element(By.ID, 'document-diff-form')
        first_file = self.get_driver().find_element(By.ID, 'first-file')
        second_file = self.get_driver().find_element(By.ID, 'second-file')
        start_button = self.get_driver().find_element(By.ID, 'start-document-diff')

        self.assertTrue(form.get_attribute('action').endswith('/document_diff/compare'))
        self.assertEqual(first_file.get_attribute('accept'), '.doc,.docx,.md,.odt')
        self.assertEqual(second_file.get_attribute('accept'), '.doc,.docx,.md,.odt')
        self.assertFalse(start_button.is_enabled())

    def test_change_document_format(self):
        self.begin()

        format_pptx = self.get_driver().find_element(By.CSS_SELECTOR, 'input[name="format"][value="pptx"]')
        self.get_driver().find_element(By.XPATH, '//input[@name="format" and @value="pptx"]/parent::label').click()
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.find_element(By.ID, 'first-file').get_attribute('accept') == '.ppt,.pptx,.odp'
        )

        self.assertTrue(format_pptx.is_selected())
        self.assertEqual(
            self.get_driver().find_element(By.ID, 'second-file').get_attribute('accept'), '.ppt,.pptx,.odp'
        )

    def test_open_system_document_search(self):
        self.begin()

        self.get_driver().find_element(By.CSS_SELECTOR, '.find-system-document[data-side="first"]').click()
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, 'system-document-search')))
        table = self.get_driver().find_element(By.ID, 'document-diff-table')

        self.assertTrue(table.is_displayed())
