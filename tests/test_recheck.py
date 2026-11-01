import time

from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class RecheckTestSelenium(BasicSeleniumTest):
    def test_recheck_file(self):
        check_id = self.open_statistic()
        if check_id:
            URL = self.get_url(f"/recheck/{check_id}")
            self.get_driver().get(URL)
            obj = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "results_title")))
            if "Производится проверка файла" in obj.text:
                start_time = time.time()
                max_time = 240
                while (time.time() - start_time) < max_time:
                    time.sleep(10)
                    try:
                        obj = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.ID, "results_table"))
                        )
                        if obj is not None:
                            self.assertNotEquals(obj, None)
                            return
                    except Exception:
                        continue
                self.fail("Result of check is not found")
            else:
                self.fail("No checking status after /recheck")
        else:
            self.skipTest("No check in system for testing recheck")
