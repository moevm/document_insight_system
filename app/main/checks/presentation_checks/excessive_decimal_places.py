import re
from ..base_check import BasePresCriterion, answer
from utils.decimal_checker import DecimalPlacesChecker, DocumentType


class PresExcessiveDecimalPlacesCheck(BasePresCriterion):
    description = 'Проверка на избыточное количество десятичных знаков в числах'
    label = "Проверка на избыточное количество десятичных знаков"
    id = 'pres_excessive_decimal_places_check'

    def __init__(self, file_info, max_decimal_places=2, max_number_of_violations=1):
        super().__init__(file_info)
        self.max_decimal_places = max_decimal_places
        self.max_number_of_violations = max_number_of_violations
        self.checker = DecimalPlacesChecker(max_decimal_places, DocumentType.PRESENTATION)

    def check(self):
       
        detected_slides = {}
        total_violations = 0
        
        for slide_num, slide_text in enumerate(self.file.get_text_from_slides()):
            lines = re.split(r'\n', slide_text)
            
            slide_violations = self.checker.find_violations_in_lines(lines)
            
            for line_idx, number_str, decimal_places, line in slide_violations:
                total_violations += 1
                
                if slide_num not in detected_slides:
                    detected_slides[slide_num] = []
                
                violation_msg = self.checker.format_violation_message(
                    line_idx, line, number_str, decimal_places
                )
                detected_slides[slide_num].append(violation_msg)
        
        if total_violations > self.max_number_of_violations:
            result_str = self.checker.format_failure_message(
                total_violations, 
                detected_slides, 
                format_page_link_fn=self.format_page_link
            )
            result_score = 0
        else:
            result_str = self.checker.format_success_message()
            result_score = 1
        
        return answer(result_score, result_str)
