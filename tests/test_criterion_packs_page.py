from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException

class CriterionPacksTestSelenium(BasicSeleniumTest):

    def begin(self):
        self.authorization()
        URL = self.get_url('/criterion_packs')
        self.get_driver().get(URL)
        self.get_driver().implicitly_wait(30)

    def pack_changing(self):
        form = self.get_driver().find_element(By.ID, 'raw_criterions')
        text_form = form.get_attribute('value')
        form.clear()
        form.send_keys(text_form)
        save_button = self.get_driver().find_element(By.ID, 'pack_submit_button')
        save_button.click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "success-text")))
        success_text = self.get_driver().find_element(By.ID, "success-text")
        self.assertNotEqual(success_text, None)

    def pack_wrong_changing(self):
        form = self.get_driver().find_element(By.ID, 'raw_criterions')
        form.send_keys('some_wrong_text')
        save_button = self.get_driver().find_element(By.ID, 'pack_submit_button')
        save_button.click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "error-text")))
        error_text = self.get_driver().find_element(By.ID, "error-text")
        self.assertNotEqual(error_text, None)    

    def test_open_criterions_pack_list(self):
        self.begin()
        string_in_table = self.driver.find_element(By.XPATH, "//table[contains(@class, 'table')]//tbody/tr[1]/td[4]/a")
        self.assertNotEqual(string_in_table, None)
        headers = self.driver.find_elements(By.XPATH, "//table//th")
        header_name = any("название" in header.text.lower() for header in headers)
        header_type = any('тип' in header.text.lower() for header in headers)
        header_edit = any('редактировать' in header.text.lower() for header in headers)
        self.assertTrue(header_name, 'header "название" is not found')
        self.assertTrue(header_type, 'header "тип" is not found')
        self.assertTrue(header_edit, 'header "редактировать" is not found')

        # except NoSuchElementException:
        #     empty_table = self.driver.find_element(By.CLASS_NAME, "no-records-found")
        #     self.assertNotEqual(empty_table, None)

    def test_open_new_pack(self):
        self.begin()
        part_of_link_text = "создать"
        xpath_expression = f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя'), '{part_of_link_text.lower()}')]"
        link_element = self.driver.find_element(By.XPATH, xpath_expression)
        link_element.click()
        expected_url = self.get_url('/criterion_pack')
        self.assertEqual(self.driver.current_url, expected_url)


    def test_for_one_pack(self):
        self.begin()
        string_in_table = self.driver.find_element(By.XPATH, "//table[contains(@class, 'table')]//tr[1]/td[4]/a")
        pack_name = string_in_table.get_attribute("href").split("/")[-1]
        pack_type = self.driver.find_element(By.XPATH, "//table[contains(@class, 'table')]//tr[1]/td[2]").text.replace('.', ' ').split(' ')[0]
        URL = self.get_url(f'/criterion_pack/{pack_name}')
        self.get_driver().get(URL)
        opened_pack_name = self.get_driver().find_element(By.ID, 'pack_name').get_attribute('value')
        opened_pack_type = self.get_driver().find_element(By.ID, 'file_type')
        select = Select(opened_pack_type)
        selected_type_text = select.first_selected_option.text.strip()
        self.assertEqual(pack_name, opened_pack_name)
        self.assertEqual(pack_type, selected_type_text)
        self.pack_changing()
        self.pack_wrong_changing()


    def test_pack_description(self):
        self.authorization()
        description = self.driver.find_element(By.ID, 'btn_table_info')
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "table_info")))
        table_info = self.get_driver().find_element(By.ID, "table_info")
        rows = table_info.find_elements(By.TAG_NAME, 'li')
        self.assertNotEqual(rows, None)
