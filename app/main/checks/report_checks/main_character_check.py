from ..base_check import BaseReportCriterion, answer
from .main_page_settings import ReportMainPageSetting
import re
import copy


class ReportMainCharacterCheck(BaseReportCriterion):
    label = "Проверка составляющих титульного листа, задания и календарного плана"
    description = ""
    id = "main_character_check"
    priority = True

    def __init__(self, file_info, tables_count_to_verify=8):
        super().__init__(file_info)
        self.headers = []
        self.first_check_list = None
        self.second_check_list = None
        self.tables_count_to_verify = tables_count_to_verify

    def late_init(self):
        self.headers = self.file.make_headers(self.file_type['report_type'])

    def check(self):
        self.first_check_list = copy.deepcopy(ReportMainPageSetting.FIRST_TABLE)
        self.second_check_list = copy.deepcopy(ReportMainPageSetting.SECOND_TABLE)
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        if self.tables_count_to_verify > len(self.file.tables):
            return answer(False, f"Количество таблиц на страницах титульного листа, задания и календарного плана должно быть не меньше {self.tables_count_to_verify}")
        self.late_init()
        result_str = ""
        pages = []
        for header in self.headers:
            if header["marker"] and header["main_character"]:
                pages.append(header["page"])
        for i in range(self.tables_count_to_verify):
            table = self.file.tables[i]
            extract_table = self.extract_table_contents(table)
            self.check_table(self.first_check_list, extract_table)
            self.check_table(self.second_check_list, extract_table)
        links = self.format_page_link(pages)
        for res in self.first_check_list + self.second_check_list:
            if res["found_key"] > 1 and res["key"] == "Консультант":
                links = self.format_page_link(pages[1:])
                result_str += f"На страницах {links} не нужно указывать консультантов.<br>"
            elif res["found_key"] < res["find"] and res["key"] != "Консультант":
                result_str += f"Поле '{res['key']}' не найдено на страницах {links}. Его удалось обнаружить {res['found_key']} из {res['find']} раз. Проверьте корректность всех вхождений.<br>"
            elif res["found_value"] < res["find"]:
                links = self.format_page_link(pages)
                result_str += f"Содержимое поля '{res['key']}' указано корректно {res['found_value']} из {res['find']} раз. Проверьте корректность всех вхождений на страницах {links}.<br>"
        if not result_str:
            return answer(True, 'Пройдена!')
        else:
            result_str += f'<br>Убедитесь, что вы использовали правильные формы бланков титульного листа, задания и календарного плана.' \
                          f'<br>Для бакалавров: <a href="https://drive.google.com/drive/folders/1pvv9HJIUB0VZUXteGqtLcVq6zIgZ6rbZ">Формы бланков для бакалавров</a>.' \
                          f'<br>Для магистров: <a href="https://drive.google.com/drive/folders/1KOoXzKv4Wf-XyGzOf1X8gN256sgame1D">Формы бланков для магистров</a>.'
            return answer(False, result_str)
        
    def extract_table_contents(self, table):
        contents = []
        processed_cells = set()
        for row in table.rows:
            row_text = []
            for cell in row.cells:
                if cell not in processed_cells:
                    row_text.append(cell.text.strip())
                    processed_cells.add(cell)
            contents.append(' '.join(row_text))
        return contents
    
    def calculate_find_value(self, table, index):
        count = int((len(table) - index - 2) / 2)
        if count >= 0:
            return count
        return 0
    
    def check_table(self, check_list, table):
        for item in check_list:
            flag = False
            for i, line in enumerate(table):
                if item["key"] in line:
                    flag = True
                    item["found_key"] += 1
                    if item["key"] == "Консультант":
                        if item["found_key"] == 1:
                            item["find"] += self.calculate_find_value(table, i)
                        else:
                            flag = False
                if flag:
                    for value in item["value"]:
                        if re.search(value, line):
                            item["found_value"] += 1
                            break
                    if item["key"] != "Зав. кафедрой" and item["key"] != "Консультант":
                        flag = False