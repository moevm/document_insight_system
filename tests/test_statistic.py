from urllib.parse import parse_qs, urlencode, urlparse

from basic_selenium_test import BasicSeleniumTest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class StatisticTestSelenium(BasicSeleniumTest):
    CHECK_LIST_URL = '/check_list'
    SCORE_INPUT = (By.CSS_SELECTOR, '.bootstrap-table-filter-control-score')
    UPLOAD_DATE_INPUT = (By.CSS_SELECTOR, '.bootstrap-table-filter-control-upload-date')
    DATA_ROWS = (By.CSS_SELECTOR, '#check-list-table tbody tr[data-index]')
    NO_RECORDS = (By.CLASS_NAME, 'no-records-found')

    # широкий диапазон, покрывающий любые даты в системе
    ALL_DATES = '01.01.2000 00:00 - 01.01.2100 00:00'
    # диапазон, в который не попадёт ни одна реальная загрузка
    NO_DATES = '01.01.1900 00:00 - 02.01.1900 00:00'

    def open_check_list(self, filters=None):
        self.authorization()
        url = self.get_url(self.CHECK_LIST_URL)
        if filters:
            url += '?' + urlencode(filters)
        self.get_driver().get(url)
        WebDriverWait(self.get_driver(), 30).until(EC.presence_of_element_located(self.SCORE_INPUT))

    def input_value(self, locator):
        return self.get_driver().find_element(*locator).get_attribute('value')

    def wait_for_rows_or_empty(self):
        WebDriverWait(self.get_driver(), 30).until(
            lambda driver: driver.find_elements(*self.DATA_ROWS) or driver.find_elements(*self.NO_RECORDS)
        )

    def get_data_rows(self):
        return self.get_driver().find_elements(*self.DATA_ROWS)

    def first_row_score(self):
        return self.get_data_rows()[0].find_elements(By.TAG_NAME, 'td')[-1].text.strip()

    @staticmethod
    def url_param(url, name):
        values = parse_qs(urlparse(url).query).get(name)
        return values[0] if values else None

    def test_open_statistic(self):
        self.authorization()
        URL = self.get_url('/check_list')
        self.get_driver().get(URL)
        self.get_driver().implicitly_wait(30)
        try:
            string_in_table = self.driver.find_element(By.XPATH, "//table[@id='check-list-table']//tr/td/a")
            self.assertNotEqual(string_in_table, None)
        except NoSuchElementException:
            empty_table = self.driver.find_element(*self.NO_RECORDS)
            self.assertNotEqual(empty_table, None)

    # score

    def test_score_filter_is_saved_in_url(self):
        self.open_check_list()

        score_input = self.get_driver().find_element(*self.SCORE_INPUT)
        score_input.clear()
        score_input.send_keys('-1')

        WebDriverWait(self.get_driver(), 10).until(
            lambda driver: self.url_param(driver.current_url, 'filter_score') == '-1'
        )

    def test_score_range_filter_is_saved_in_url(self):
        self.open_check_list()

        score_input = self.get_driver().find_element(*self.SCORE_INPUT)
        score_input.clear()
        score_input.send_keys('0.5-0.89')

        WebDriverWait(self.get_driver(), 10).until(
            lambda driver: self.url_param(driver.current_url, 'filter_score') == '0.5-0.89'
        )

    def test_score_filter_is_restored_from_url(self):
        self.open_check_list(filters={'filter_score': '-1'})

        WebDriverWait(self.get_driver(), 10).until(lambda driver: self.input_value(self.SCORE_INPUT) == '-1')
        self.assertEqual(self.url_param(self.get_driver().current_url, 'filter_score'), '-1')

    def test_score_range_filter_is_restored_from_url(self):
        self.open_check_list(filters={'filter_score': '0.5-0.89'})

        WebDriverWait(self.get_driver(), 10).until(lambda driver: self.input_value(self.SCORE_INPUT) == '0.5-0.89')

    def test_score_filter_filters_rows(self):
        self.open_check_list()
        self.wait_for_rows_or_empty()
        if not self.get_data_rows():
            self.skipTest('No checks in system for score filter test')

        score = self.first_row_score()
        if not score:
            self.skipTest('First row has no score for score filter test')

        self.open_check_list(filters={'filter_score': score})
        self.wait_for_rows_or_empty()

        filtered_rows = self.get_data_rows()
        self.assertTrue(filtered_rows)
        for row in filtered_rows:
            self.assertEqual(row.find_elements(By.TAG_NAME, 'td')[-1].text.strip(), score)

    # dates

    def test_upload_date_filter_is_restored_from_url(self):
        self.open_check_list(filters={'filter_upload-date': self.ALL_DATES})

        WebDriverWait(self.get_driver(), 10).until(
            lambda driver: self.input_value(self.UPLOAD_DATE_INPUT) == self.ALL_DATES
        )
        self.assertEqual(self.url_param(self.get_driver().current_url, 'filter_upload-date'), self.ALL_DATES)

    def test_upload_date_filter_is_saved_in_url(self):
        self.open_check_list()

        date_input = self.get_driver().find_element(*self.UPLOAD_DATE_INPUT)
        self.get_driver().execute_script(
            "arguments[0]._flatpickr.setDate(['01.01.2020 00:00', '01.01.2030 00:00'], true);",
            date_input,
        )

        expected = WebDriverWait(self.get_driver(), 10).until(
            lambda driver: self.input_value(self.UPLOAD_DATE_INPUT) or False
        )
        WebDriverWait(self.get_driver(), 10).until(
            lambda driver: self.url_param(driver.current_url, 'filter_upload-date') == expected
        )

    def test_upload_date_filter_filters_rows(self):
        self.open_check_list()
        self.wait_for_rows_or_empty()
        total_rows = len(self.get_data_rows())
        if total_rows == 0:
            self.skipTest('No checks in system for upload date filter test')

        self.open_check_list(filters={'filter_upload-date': self.ALL_DATES})
        self.wait_for_rows_or_empty()
        self.assertEqual(len(self.get_data_rows()), total_rows)

        self.open_check_list(filters={'filter_upload-date': self.NO_DATES})
        self.wait_for_rows_or_empty()
        self.assertEqual(len(self.get_data_rows()), 0)
        self.assertNotEqual(self.get_driver().find_elements(*self.NO_RECORDS), [])
