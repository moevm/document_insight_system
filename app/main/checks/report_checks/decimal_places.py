from app.utils.decimal_places_check import DecimalPlacesCheck
from ..base_check import BaseReportCriterion, answer

class ReportDecimalPlacesCheck(BaseReportCriterion):
    label = 'Проверка на избыточное количество десятичных знаков'
    _description = 'Проверка на избыточное количество десятичных знаков в числах'
    id = 'decimal_places_check'

    def __init__(self, file_info, max_decimal_places=2, max_violations=3):
        super().__init__(file_info)
        self.checker = DecimalPlacesCheck(file_info, max_decimal_places, max_violations)

    def check(self):
        total_violations, detected_pages = self.checker.find_violations_in_texts(self.file.pdf_file.get_text_on_page().items())
        result_str, result_score = self.checker.get_result_msg_and_score(total_violations, detected_pages, self.format_page_link)
        return answer(result_score, result_str)
