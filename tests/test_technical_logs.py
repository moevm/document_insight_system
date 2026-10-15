from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TechLogsTestSelenium(BasicSeleniumTest):
    MAX_TIME = 30

    def _login(self, login, password):
        driver = self.get_driver()
        driver.get(self.get_url('/login/'))
        WebDriverWait(driver, self.MAX_TIME).until(
            EC.presence_of_element_located((By.ID, "login_text_field"))
        )
        driver.find_element(By.ID, "login_text_field").send_keys(login)
        driver.find_element(By.ID, "password_text_field").send_keys(password)
        driver.find_element(By.ID, "login_button").click()
        WebDriverWait(driver, self.MAX_TIME).until(EC.url_contains("/upload/"))

    def _open_results_and_logs(self, check_id):
        driver = self.get_driver()
        driver.get(self.get_url(f'/results/{check_id}'))
        
        WebDriverWait(driver, self.MAX_TIME).until(
            EC.presence_of_element_located((By.ID, "enable-debug-logs"))
        )
        
        driver.find_element(By.ID, "enable-debug-logs").click()
        driver.find_element(By.ID, "toggle-logs").click()
        
        WebDriverWait(driver, self.MAX_TIME).until(
            EC.visibility_of_element_located((By.ID, "check-diagnostics"))
        )
        
        WebDriverWait(driver, self.MAX_TIME).until(
            EC.visibility_of_element_located((By.ID, "diag-last-error"))
        )

    def _get_last_check_id(self):
        driver = self.get_driver()
        
        driver.get(self.get_url('/check_list'))
        
        WebDriverWait(driver, self.MAX_TIME).until(
            EC.presence_of_element_located((By.ID, "check-list-table"))
        )
        
        first_link = driver.find_element(By.CSS_SELECTOR,"#check-list-table tbody tr:first-child a")
        
        href = first_link.get_attribute("href")
        
        check_id = href.split("/")[-1]
        
        return check_id

    def test_logs_loaded(self):
        login, password = self.param[1:3]
        check_id = self._get_last_check_id()
        
        self._login(login, password)
        self._open_results_and_logs(check_id)
        
        driver = self.get_driver()
        
        last_err = driver.find_element(By.ID, "diag-last-error").text
        logs_text = driver.find_element(By.ID, "logs-text").text
        logs_stage = driver.find_element(By.ID, "diag-stage").text
        
        
        self.assertNotIn("не удалось загрузить логи", last_err)
        self.assertNotIn("не удалось загрузить логи", logs_text)
        self.assertNotIn("status=500", last_err)
        self.assertNotIn("status=n/a", last_err)
        self.assertNotEqual(logs_stage.strip(), "—")
        self.assertNotEqual(logs_stage.strip(), "")
