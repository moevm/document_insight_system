import time
from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By

class ReportLoadTestSelenium(BasicSeleniumTest):

    def upload_report(self, report_ext):
        self.authorization()
        report = report_ext
        URL = self.getUrl('/upload')
        self.getDriver().get(URL)
        self.getDriver().implicitly_wait(480)
        obj = self.getDriver().find_element(By.XPATH, "/html/body/div/div[2]/div/p/b")
        if obj.text == 'BaseReportCriterionPack':
            form_for_load = self.getDriver().find_element(By.CSS_SELECTOR, 'input[type=file]')
            form_for_load.send_keys(report)
            load_button = self.getDriver().find_element(By.XPATH, '//*[@id="upload_upload_button"]')
            load_button.click()
            obj = self.getDriver().find_element(By.XPATH, '/html/body/div/div[2]/h4/i')
            if obj.text == 'Производится проверка файла. Примерное время: 229999.1 секунд (перезагрузите страницу)':
                start_time = time.time()
                max_time = 240
                while time.time() - start_time < max_time:
                    time.sleep(10)
                    self.getDriver().refresh()
                    obj = self.getDriver().find_element(By.ID, 'results_table')
                    if obj is not None:
                        break
                self.assertNotEquals(obj, None)
            else:
                self.fail("file didn't upload")
        else:
            self.skipTest("Current criteria pack is not for report")


    def test_report_load_docx(self):
        self.upload_report(self.param[3])

    def test_report_load_doc(self):
        self.upload_report(self.param[4])    
