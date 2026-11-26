import os
from datetime import datetime, timezone

from basic_selenium_test import BasicSeleniumTest
from bson import ObjectId
from pymongo import MongoClient
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TechLogsTestSelenium(BasicSeleniumTest):
    MAX_TIME = 30

    def _login(self, login, password):
        driver = self.get_driver()
        driver.delete_all_cookies()
        driver.get(self.get_url('/login/'))
        WebDriverWait(driver, self.MAX_TIME).until(EC.presence_of_element_located((By.ID, "login_text_field")))
        driver.find_element(By.ID, "login_text_field").send_keys(login)
        driver.find_element(By.ID, "password_text_field").send_keys(password)
        driver.find_element(By.ID, "login_button").click()
        WebDriverWait(driver, self.MAX_TIME).until(EC.url_contains("/upload/"))

    def _open_results_and_logs(self, check_id):
        driver = self.get_driver()
        driver.get(self.get_url(f'/results/{check_id}'))

        WebDriverWait(driver, self.MAX_TIME).until(EC.presence_of_element_located((By.ID, "enable-debug-logs"))).click()

        WebDriverWait(driver, self.MAX_TIME).until(EC.element_to_be_clickable((By.ID, "toggle-logs"))).click()

        WebDriverWait(driver, self.MAX_TIME).until(EC.visibility_of_element_located((By.ID, "check-diagnostics")))

        WebDriverWait(driver, self.MAX_TIME).until(EC.visibility_of_element_located((By.ID, "diag-last-error")))

    def _create_check(self, messages):
        client = MongoClient(
            os.environ.get("TEST_MONGODB_URI", "mongodb://mongodb:27017"), serverSelectionTimeoutMS=5000
        )
        db = client['dis-db']
        check_id = ObjectId()

        self.addCleanup(client.close)
        self.addCleanup(db.checks.delete_one, {"_id": check_id})
        self.addCleanup(db.logs.delete_many, {"check_id": str(check_id)})
        db.checks.insert_one(
            {
                "_id": check_id,
                "user": self.param[1],
                "filename": "test.docx",
                "file_type": {"type": "report", "report_type": "VKR"},
                "criteria": "test",
                "enabled_checks": [],
                "score": 1,
                "is_ended": True,
            }
        )
        for stage, level, message in messages:
            db.logs.insert_one(
                {
                    "timestamp": datetime.now(timezone.utc),
                    "serviceName": "selenium-test",
                    "levelname": level,
                    "message": message,
                    "pathname": "test",
                    "lineno": 1,
                    "check_id": str(check_id),
                    "stage": stage,
                }
            )
        return str(check_id)

    def test_logs_loaded(self):
        login, password = self.param[1:3]
        parse_message = "Тестовый лог парсинга"
        check_message = "Тестовое предупреждение проверки"
        check_id = self._create_check([("parse", "INFO", parse_message), ("check", "WARNING", check_message)])

        self._login(login, password)
        self._open_results_and_logs(check_id)

        driver = self.get_driver()

        wait = WebDriverWait(driver, self.MAX_TIME)
        wait.until(EC.text_to_be_present_in_element((By.ID, "logs-text"), parse_message))
        wait.until(EC.text_to_be_present_in_element((By.ID, "logs-text"), check_message))
        wait.until(EC.text_to_be_present_in_element((By.ID, "diag-last-error"), check_message))
        logs_text = driver.find_element(By.ID, "logs-text").text
        self.assertTrue(any("parse" in line and parse_message in line for line in logs_text.splitlines()))
        self.assertTrue(any("check" in line and check_message in line for line in logs_text.splitlines()))
        self.assertEqual(driver.find_element(By.ID, "diag-stage").text.strip(), "check")

    def test_logs_without_warnings_or_errors(self):
        login, password = self.param[1:3]
        message = "Тестовый лог парсинга"
        check_id = self._create_check([("parse", "INFO", message)])

        self._login(login, password)
        self._open_results_and_logs(check_id)
        driver = self.get_driver()
        wait = WebDriverWait(driver, self.MAX_TIME)
        wait.until(EC.text_to_be_present_in_element((By.ID, "logs-text"), message))
        wait.until(EC.text_to_be_present_in_element((By.ID, "diag-last-error"), "WARNING/ERROR не найдено."))
        self.assertEqual(driver.find_element(By.ID, "diag-stage").text.strip(), "—")
