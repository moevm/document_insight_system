import unittest
import os
from parameterized import parameterized_class
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import url_to_be, element_to_be_clickable, invisibility_of_element

@parameterized_class([
    {
        "template": 'test.odt',
        "table": 'table.csv',
        'verification_mes': "<p>'age' not defined in the template</p><p>'address' not defined in the csv</p>",
        'no_output_files': 3
    },
    {
        "template": 'test.docx',
        "table": 'table.csv',
        'verification_mes': '<p>Verification done without warning</p>',
        'no_output_files': 3
    },
    {
        "template": 'test.odp',
        "table": 'table.csv',
        'verification_mes': "<p>'asd' not defined in the csv</p>",
        'no_output_files': 3
    },
    {
        "template": 'test.pptx',
        "table": 'table.csv',
        'verification_mes': "<p>'asd' not defined in the csv</p>",
        'no_output_files': 3
    },
    {
        "template": 'test.ods',
        "table": 'table.csv',
        'verification_mes': "<p>'age' not defined in the template</p>",
        'no_output_files': 3
    },
    {
        "template": 'test.xlsx',
        "table": 'table.csv',
        'verification_mes': "<p>'age' not defined in the template</p>",
        'no_output_files': 3
    },
])
class FunctionalTests(unittest.TestCase):
    def setUp(self):
        options = Options()
        options.headless = True
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1420,1080')
        options.add_argument('--allow-insecure-localhost')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = Chrome(options=options)

        self.template_folder = os.path.abspath('./app/tests/templates')
        self.data_folder = os.path.abspath('./app/tests/data')
        
        

    def tearDown(self):
        self.driver.quit()


    def test_files(self):
        try:
            self.driver.get("http://localhost:5000/")  
        except:
            self.driver.get("http://web:5000/")
            
        if(len(self.driver.find_element(By.TAG_NAME, 'body').get_attribute('innerHTML'))==0):
            self.driver.get("http://web:5000/")
        
        self.driver.find_element(
            By.CSS_SELECTOR, "#navbarNav ul li:first-child a").click()
        
        # print(self.driver.current_url)
        # self.driver.add_cookie({'name' : '_LOCALE_', 'value' : 'en'})
        self.driver.refresh()
        self.driver.find_element(
            By.ID, "template-file").send_keys(os.path.join(self.template_folder,self.template))
        self.driver.find_element(By.ID, "btn-upload-template").click()

        # wait until upload complete (use this template button available to press)
        WebDriverWait(self.driver, timeout=10).until(
            element_to_be_clickable((By.ID, "btn-use-template")))
        self.driver.find_element(By.ID, "btn-use-template").click()

        WebDriverWait(self.driver, timeout=10).until(
            element_to_be_clickable((By.ID, "btn-upload-data")))
        self.driver.find_element(
            By.ID, "data-table-file").send_keys(os.path.join(self.data_folder,self.table))
        self.driver.find_element(By.ID, "btn-upload-data").click()

        # wait until upload complete (use this table button available to press)
        WebDriverWait(self.driver, timeout=10).until(
            element_to_be_clickable((By.ID, "btn-verify")))
        self.driver.find_element(By.ID, "btn-verify").click()

        WebDriverWait(self.driver, timeout=20).until(
            element_to_be_clickable((By.ID, "btn-generate")))
        # check for verification result
        verification_result = self.driver.find_element(By.ID, 'verificationResult').get_attribute('innerHTML')
        self.assertEqual(verification_result, self.verification_mes)
        
        self.driver.find_element(By.ID, "btn-generate").click()
        WebDriverWait(self.driver, timeout=20).until(element_to_be_clickable(
            (By.CSS_SELECTOR, "#pills-result .row .col-md .text-center input")))
        
        no_files = len(self.driver.find_element(By.CSS_SELECTOR, '#link-files ul').find_elements_by_tag_name('li'))
        self.assertEqual(no_files, self.no_output_files)

        self.driver.find_element(
            By.CSS_SELECTOR, "#pills-result .row .col-md .text-center input").click()

