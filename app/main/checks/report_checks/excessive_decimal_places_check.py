import re
from ..base_check import BaseReportCriterion, answer
from utils.decimal_checker import DecimalPlacesChecker


class ReportExcessiveDecimalPlacesCheck(BaseReportCriterion):
    label = "Проверка на избыточное количество десятичных знаков"
    description = 'Проверка на избыточное количество десятичных знаков в числах'
    id = 'excessive_decimal_places_check'

    def __init__(self, file_info, max_decimal_places=2, max_number_of_violations=2):
        super().__init__(file_info)
        self.max_decimal_places = max_decimal_places
        self.max_number_of_violations = max_number_of_violations
        self.checker = DecimalPlacesChecker(max_decimal_places)

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        
        detected_pages = {}
        total_violations = 0
        
        for page_num, page_text in self.file.pdf_file.get_text_on_page().items():
            lines = re.split(r'\n', page_text)
            
            page_violations = self.checker.find_violations_in_lines(lines)
            
            for line_idx, number_str, decimal_places, line in page_violations:
                total_violations += 1
                
                if page_num not in detected_pages:
                    detected_pages[page_num] = []
                
                violation_msg = self.checker.format_violation_message(
                    line_idx, line, number_str, decimal_places
                )
                detected_pages[page_num].append(violation_msg)
        
        if total_violations > self.max_number_of_violations:
            result_str = self.checker.format_failure_message(
                total_violations, 
                detected_pages, 
                format_page_link_fn=self.format_page_link
            )
            result_score = 0
        else:
            result_str = self.checker.format_success_message()
            result_score = 1.0
        
        return answer(result_score, result_str)
