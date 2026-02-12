from ..base_check import BasePresCriterion, answer
from ..decimal_places_check import DecimalPlacesCheck

class PresDecimalPlacesCheck(BasePresCriterion):
    description = 'Проверка на избыточное количество десятичных знаков в числах'
    label = 'Проверка на избыточное количество десятичных знаков'
    id = 'decimal_places_check'

    def __init__(self, file_info, max_decimal_places=2, max_violations=3):
        super().__init__(file_info)
        self.checker = DecimalPlacesCheck(file_info, max_decimal_places, max_violations)

    def check(self):    
        total_violations, detected_pages = self.checker.find_violations_in_file(enumerate(self.file.get_text_from_slides()))
        result_str, result_score = self.checker.get_result_msg_and_score(total_violations, detected_pages, self.format_page_link)
        return answer(result_score, result_str)
