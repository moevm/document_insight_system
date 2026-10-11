from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class CheckListFiltersTestSelenium(BasicSeleniumTest):
    MAX_TIME = 30
    FILTER_FIELDS = [
        ("filename", "test.docx"),
        ("criteria", "VKR"),
        ("user", "admin"),
        ("score", "1.0"),
    ]

    def _login_and_open_check_list(self, login, password):
        driver = self.get_driver()

        URL = self.get_url('/login/')
        driver.get(URL)
        WebDriverWait(driver, self.MAX_TIME).until(EC.presence_of_element_located((By.ID, "login_text_field")))

        login_field = driver.find_element(By.ID, "login_text_field")
        login_field.clear()
        login_field.send_keys(login)

        password_field = driver.find_element(By.ID, "password_text_field")
        password_field.clear()
        password_field.send_keys(password)

        login_button = driver.find_element(By.ID, "login_button")
        login_button.click()

        WebDriverWait(driver, self.MAX_TIME).until(EC.url_contains("/upload/"))

        URL = self.get_url('/check_list')
        driver.get(URL)
        WebDriverWait(driver, self.MAX_TIME).until(EC.presence_of_element_located((By.ID, "check-list-table")))

    def _type_filter(self, field_name, value):
        driver = self.get_driver()
        selector = f"input.bootstrap-table-filter-control-{field_name}"

        input_field = WebDriverWait(driver, self.MAX_TIME).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )

        input_field.clear()
        input_field.send_keys(value)

    def test_filters_saved_in_url(self):
        login, password = self.param[1:3]
        self._login_and_open_check_list(login, password)
        driver = self.get_driver()

        for field_name, value in self.FILTER_FIELDS:
            with self.subTest(field=field_name, value=value):
                URL = self.get_url('/check_list')
                driver.get(URL)
                WebDriverWait(driver, self.MAX_TIME).until(EC.presence_of_element_located((By.ID, "check-list-table")))

                self._type_filter(field_name, value)

                expected_param = f"filter_{field_name}={value}"
                WebDriverWait(driver, self.MAX_TIME).until(EC.url_contains(expected_param))
                self.assertIn(expected_param, driver.current_url)

    def test_filters_restored_from_url(self):
        driver = self.get_driver()
        login, password = self.param[1:3]
        self._login_and_open_check_list(login, password)

        for field_name, value in self.FILTER_FIELDS:
            with self.subTest(field=field_name, value=value):
                URL = self.get_url(f'/check_list?filter_{field_name}={value}')
                driver.get(URL)

                WebDriverWait(driver, self.MAX_TIME).until(EC.presence_of_element_located((By.ID, "check-list-table")))

                selector = f"input.bootstrap-table-filter-control-{field_name}"
                input_field = driver.find_element(By.CSS_SELECTOR, selector)
                self.assertEqual(input_field.get_attribute("value"), value)
