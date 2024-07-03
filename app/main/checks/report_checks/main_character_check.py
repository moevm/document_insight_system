from ..base_check import BaseReportCriterion, answer
from .main_page_settings import ReportMainPageSetting
import re

class ReportMainCharacterCheck(BaseReportCriterion):
    label = "Проверка составляющих титульного листа, задания и календарного плана"
    description = ""
    id = "main_character_check"
    priority = True

    def __init__(self, file_info):
        super().__init__(file_info)
        self.headers = []
        self.first_check_list = ReportMainPageSetting.FIRST_TABLE
        self.second_check_list = ReportMainPageSetting.SECOND_TABLE
        

    def late_init(self):
        self.headers = self.file.make_headers(self.file_type['report_type'])

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        self.late_init()
        result_str = ""
        pages = []
        for header in self.headers:
            if header["marker"] and header["main_character"]:
                pages.append(header["page"])
        for page in range(min(pages), max(pages) + 1):
            self.check_first_table(page)
            self.check_second_table(page)
        for res in self.first_check_list + self.second_check_list:
            if res["found"] != res["find"]:
                print("="*100)
                print(pages)
                print(res)
                print("="*100)
                if res["found"] > res["find"] and res["key"] == "Консультант":
                    links = self.format_page_link(res["page"][1:])
                    result_str += f"На страниц(е/ах) {links} не нужно указывать консультантов.<br>"
                elif res["find"] == len(res["page"]) and len(res["page"]):
                    links = self.format_page_link(res["page"])
                    result_str += f"На страниц(е/ах) {links} содержимое поля '{res['key']}' указано корректно {res['found']} из {res['find']} раз. Проверьте корректность всех вхождений.<br>"
                elif res["found"] < res["find"]:
                    links = self.format_page_link(pages)
                    result_str += f"Поле '{res['key']}' или его содержимое указано корректно {res['found']} из {res['find']} раз. Проверьте корректность всех вхождений на страницах {links}.<br>"
        if not result_str:
            return answer(True, 'Пройдена!')
        else:
            result_str += f'<br>Убедитесь, что вы использовали правильные формы бланков титульного листа, задания и календарного плана.' \
                          f'<br>Для бакалавров: <a href="https://drive.google.com/drive/folders/1pvv9HJIUB0VZUXteGqtLcVq6zIgZ6rbZ">Формы бланков для бакалавров</a>.' \
                          f'<br>Для магистров: <a href="https://drive.google.com/drive/folders/1KOoXzKv4Wf-XyGzOf1X8gN256sgame1D">Формы бланков для магистров</a>.'
            return answer(False, result_str)
            
    def check_first_table(self, page):
        text_on_page = self.file.pdf_file.text_on_page[page].replace("\n", "")
        for item in self.first_check_list:
            key = item["key"]
            index = text_on_page.find(key)
            if index != -1:
                item["page"].append(page)
                if any(value in text_on_page[index:] for value in item["value"]):
                    item["found"] += 1

    def check_second_table(self, page):
        text_on_page = self.file.pdf_file.text_on_page[page].split("\n")
        for line in text_on_page:
            for item in self.second_check_list:
                key = item["key"]
                if key in line:
                    item["page"].append(page)
                    match = re.search(item["value"][0], line)
                    if match:
                        print(line,page)
                        end_index = match.end()
                        if ',' in line[end_index:]:
                            if re.search(item["value"][1], line[end_index:]):
                                item["found"] += 1
                        else:
                            item["found"] += 1
                    else:
                        print("((()))",line,page)