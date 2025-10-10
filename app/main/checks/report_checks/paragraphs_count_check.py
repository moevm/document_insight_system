import re
from .style_check_settings import StyleCheckSettings
from ..base_check import BaseReportCriterion, answer

class ReportParagraphsCountCheck(BaseReportCriterion):
    label = "Проверка количества абзацев в главах и их подразделах"
    description = ""
    id = "paragraphs_count_check"

    def __init__(self, file_info, min_paragraphs_in_unnumbered_section=5, min_paragraphs_in_section=10, 
                 min_paragraphs_in_subsection=5, min_paragraphs_in_subsubsection=1):
        super().__init__(file_info)
        self.min_count_paragraphs = {
            "unnumbered_section": min_paragraphs_in_unnumbered_section,
            "section": min_paragraphs_in_section,
            "subsection": min_paragraphs_in_subsection,
            "subsubsection": min_paragraphs_in_subsubsection
        }
        self.heading_styles = []
        self.paragraphs_count = []
        self.headers = []

    def late_init(self):
        self.headers = self.file.make_chapters(self.file_type['report_type'])

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        
        self.late_init()
        result = True
        result_str = ""
        
        if not self.headers:
            return answer(False, "Не найдено ни одного заголовка.<br><br>Проверьте корректность использования стилей.")
        
        for item in StyleCheckSettings.VKR_CONFIG:
            self.heading_styles.append(item["docx_style"])
        
        self.find_paragraphs_count()
        
        for obj in self.paragraphs_count:
            if obj["paragraphs"] < obj["min"]:
                result = False
                result_str += (f'Раздел "{obj["name"]}" содержит {obj["paragraphs"]} абзацев '
                            f'(не считая рисунки и таблицы), что меньше минимальной рекомендуемой '
                            f'длины раздела в {obj["min"]} абзацев.<br>')
        return answer(result, result_str if result_str else "Пройдена!")

    def find_paragraphs_count(self):
        i = 0
        while i < len(self.headers):
            if "ПРИЛОЖЕНИЕ" in self.headers[i]["text"]:
                break
            
            if self.headers[i]["style"] == self.heading_styles[0][0] and not re.search(r'\d', self.headers[i]["text"]):
                count_lists_section, ignored_paragraphs = self.find_lists_and_captions(self.headers[i]["child"])
                self.paragraphs_count.append({
                    "name": self.headers[i]["text"], 
                    "min": self.min_count_paragraphs["unnumbered_section"],
                    "paragraphs": len(self.headers[i]["child"]) - ignored_paragraphs + count_lists_section, 
                    "lists": count_lists_section
                })
                
            elif self.headers[i]["style"] == self.heading_styles[1][0]:
                count_lists_section, ignored_paragraphs = self.find_lists_and_captions(self.headers[i]["child"])
                section_count = len(self.headers[i]["child"]) - ignored_paragraphs + count_lists_section
                
                j = i + 1
                while j < len(self.headers) and self.headers[j]["style"] == self.heading_styles[1][1]:
                    count_lists_subsection, ignored_paragraphs = self.find_lists_and_captions(self.headers[j]["child"])
                    subsection_count = len(self.headers[j]["child"]) - ignored_paragraphs + count_lists_subsection
                    
                    k = j + 1
                    while k < len(self.headers) and self.headers[k]["style"] == self.heading_styles[1][2]:
                        count_lists_subsubsection, ignored_paragraphs = self.find_lists_and_captions(self.headers[k]["child"])
                        subsubsection_count = len(self.headers[k]["child"]) - ignored_paragraphs + count_lists_subsubsection
                        subsection_count += subsubsection_count
                        count_lists_subsection += count_lists_subsubsection
                        
                        self.paragraphs_count.append({
                            "name": self.headers[k]["text"], 
                            "min": self.min_count_paragraphs["subsubsection"],
                            "paragraphs": subsubsection_count, 
                            "lists": count_lists_subsubsection
                        })
                        k += 1
                    
                    section_count += subsection_count    
                    count_lists_section += count_lists_subsection 
                    
                    self.paragraphs_count.append({
                        "name": self.headers[j]["text"], 
                        "min": self.min_count_paragraphs["subsection"],
                        "paragraphs": subsection_count, 
                        "lists": count_lists_subsection
                    })
                    j = k
                
                self.paragraphs_count.append({
                    "name": self.headers[i]["text"], 
                    "min": self.min_count_paragraphs["section"],
                    "paragraphs": section_count, 
                    "lists": count_lists_section
                })
                i = j - 1
                
            i += 1

    def find_lists_and_captions(self, paragraphs):
        ignored_paragraphs = 0
        count_lists = 0
        for paragraph in paragraphs:
            if paragraph["style"].find("вкр_подпись") != -1:
                ignored_paragraphs += 1
            # necessary search lists
        return count_lists, ignored_paragraphs
