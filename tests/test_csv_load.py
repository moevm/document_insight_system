import os
import time
import pandas as pd
import requests
from basic_selenium_test import BasicSeleniumTest
from selenium.webdriver.common.by import By


def get_downloads_path():
    if os.name == 'nt':
        return os.path.join(os.environ['USERPROFILE'], 'Downloads')
    else:
        return os.path.join(os.environ['HOME'], 'Downloads')

def get_latest_csv(dir):
    files = [os.path.join(dir, f) for f in os.listdir(dir)]
    latest_file = max(files, key=os.path.getmtime)
    return latest_file


class CsvDownloadTestSelenium(BasicSeleniumTest):

    def test_http_connection(self):
        csv_url = 'http://localhost:8080/get_csv'

        response = requests.get(csv_url)
        self.assertEqual(response.status_code, 200, f"Ошибка при скачивании CSV файла. Статус: {response.status_code}")


    def test_csv_add_download(self):
        self.authorization()
        URL = self.get_url('/check_list')
        self.get_driver().get(URL)
        self.get_driver().implicitly_wait(30)

        csv_button = self.driver.find_element(By.XPATH, '//button[text()="CSV"]')
        csv_button.click()

        time.sleep(10)

        download_dir = get_downloads_path()

        csv_file = get_latest_csv(download_dir)
        self.assertTrue(csv_file.endswith('.csv'), "Скачанный файл не является CSV файлом.")



    def test_csv_content(self):
        download_dir = get_downloads_path()
        csv_file = get_latest_csv(download_dir)
        df = pd.read_csv(csv_file)
        expected_columns =['_id', 'filename', 'criteria', 'user', 'upload-date', 'score']
        for column in expected_columns:
            self.assertIn(column, df.columns, f"Столбец '{column}' не найден в файле CSV.")

    def test_csv_download_and_filter(self):
        file_name_input = self.driver.find_element(By.CSS_SELECTOR, 'input.form-control.bootstrap-table-filter-control-filename.search-input')

        file_name_input.send_keys('example_of_report.docx')
        file_name_sort_button = self.driver.find_element(By.XPATH, '//div[contains(@class, "th-inner") and contains(@class, "sortable") and text()="File name"]')
        file_name_sort_button.click()

        time.sleep(5)

        csv_button = self.driver.find_element(By.XPATH, '//button[text()="CSV"]')
        csv_button.click()

        time.sleep(10)

        download_dir = get_downloads_path()
        latest_file = get_latest_csv(download_dir)

        df = pd.read_csv(latest_file)
        filtered_by_name = df[df['filename'] == 'example_of_report.docx']
        self.assertTrue(len(filtered_by_name) > 0, "Нет данных, отфильтрованных по имени файла.")
