import time
from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By

class ReportLoadTestSelenium(BasicSeleniumTest):

    def test_pres_load(self):
        self.authorization()
        report = self.param[4]
        URL = self.getUrl('/upload')
        self.getDriver().get(URL)
        self.getDriver().implicitly_wait(30)
        obj = self.getDriver().find_element(By.XPATH, "/html/body/div/div[2]/div/p/b")
        if obj.text == 'BaseReportCriterionPack':
            form_for_load = self.getDriver().find_element(By.CSS_SELECTOR, 'input[type=file]')
            form_for_load.send_keys(report)
            load_button = self.getDriver().find_element(By.XPATH, '//*[@id="upload_upload_button"]')
            load_button.click()
            obj = self.getDriver().find_element(By.XPATH, '/html/body/div/div[2]/h4/i')
            if obj.text == 'Производится проверка файла. Примерное время: 229999.1 секунд (перезагрузите страницу)':
                time.sleep(10)
                self.getDriver().refresh()
                self.getDriver().implicitly_wait(30)
                obj = self.getDriver().find_element(By.ID, 'results_table')
                self.assertNotEquals(obj, None)
            else:
                self.fail("file didn't upload")
        else:
            self.fail("Check criteria pack")
