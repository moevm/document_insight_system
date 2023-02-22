from ..base_check import BaseReportCriterion, answer
from .style_check_settings import StyleCheckSettings


class ReportNeededHeaders(BaseReportCriterion):
    description = "Проверка наличия обязательных заголовков в отчете"
    id = 'needed_headers_check'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.headers = self.file.chapters
        self.config = 'VKR_HEADERS' if (self.file_type['report_type'] == 'VKR') else 'LR_HEADERS'
        self.patterns = StyleCheckSettings.CONFIGS.get(self.config)[0]["headers"]

    def check(self):
        patterns = self.patterns
        for header in self.headers:
            header_text = header["text"].lower()
            for pattern in self.patterns:
                if header_text.find(pattern.lower()):
                   patterns.remove(pattern)

        result_score = 0
        if len(patterns) == 0:
            result_score = 1
        if result_score:
            return answer(result_score, "Все необходимые заголовки обнаружены!")
        else:
            result_str = '</li><li>'.join([k for k in patterns])
            return answer(result_score,
                          f'Не найдены следующие обязательные заголовки: <ul><li>{result_str}</ul>')