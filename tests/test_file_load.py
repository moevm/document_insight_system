import time
from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class FileLoadTestSelenium(BasicSeleniumTest):

    def upload_file(self, report_ext):
        report = report_ext
        form_for_load = self.get_driver().find_element(By.CSS_SELECTOR, 'input[type=file]')
        form_for_load.send_keys(report)
        load_button = self.get_driver().find_element(By.XPATH, '//*[@id="upload_upload_button"]')
        load_button.click()
        obj = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/h4/i')))
        if obj.text.startswith('Производится проверка файла'):
            start_time = time.time()
            max_time = 240
            while time.time() - start_time < max_time:
                time.sleep(10)
                self.get_driver().refresh()
                obj = self.get_driver().find_element(By.ID, 'results_table')
                if obj is not None:
                    break
            self.assertNotEquals(obj, None)
        else:
            self.fail("file didn't upload")


    def check_pack(self):
        self.authorization()
        URL = self.get_url('/upload')
        self.get_driver().get(URL)
        self.get_driver().implicitly_wait(30)
        # obj = self.get_driver().find_element(By.XPATH, "/html/body/div/div[2]/div/p/b")
        obj = self.get_driver().find_element(By.ID, "criteria_pack_name")
        return obj.text

    def test_report_load_docx(self):
        obj = self.check_pack()
        if obj == 'BaseReportCriterionPack':
            self.upload_file(self.param[3])
        else:
            self.skipTest("Current criteria pack is not for report") 

    def test_report_load_doc(self):
        obj = self.check_pack()
        if obj == 'BaseReportCriterionPack':
            self.upload_file(self.param[4])
        else:
            self.skipTest("Current criteria pack is not for report")     

    def test_report_load_pres(self):
        obj = self.check_pack()
        if obj == 'BasePresentationCriterionPack':
            self.upload_file(self.param[5])
        else:
            self.skipTest("Current criteria pack is not for pres")
