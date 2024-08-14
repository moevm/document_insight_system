from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

class CriterionPacksTestSelenium(BasicSeleniumTest):


    def begin(self):
        self.authorization()
        URL = self.get_url('/criterion_packs')
        self.get_driver().get(URL)
        self.get_driver().implicitly_wait(30)

    def test_open_criterions_pack_list(self):
        self.begin()
        string_in_table = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/table/tbody/tr[1]/td[4]/a")
        self.assertNotEqual(string_in_table, None)
        # except NoSuchElementException:
        #     empty_table = self.driver.find_element(By.CLASS_NAME, "no-records-found")
        #     self.assertNotEqual(empty_table, None)


    def test_open_one_pack(self):
        self.begin()
        string_in_table = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/table/tbody/tr[1]/td[4]/a")
        pack_name = string_in_table.get_attribute("href").split("/")[-1]
        URL = self.get_url(f'/criterion_pack/{pack_name}')
        self.get_driver().get(URL)
        obj = self.get_driver().find_element(By.ID, 'raw_criterions')
        self.assertNotEquals(obj, None)

    def test_open_new_pack(self):
        self.begin()
        part_of_link_text = "создать"
        xpath_expression = f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя'), '{part_of_link_text.lower()}')]"
        link_element = self.driver.find_element(By.XPATH, xpath_expression)
        link_element.click()
        expected_url = self.get_url('/criterion_pack')
        self.assertEqual(self.driver.current_url, expected_url)
