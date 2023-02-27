from ..base_check import BaseReportCriterion, answer
from .style_check_settings import StyleCheckSettings


class ReportNeededHeaders(BaseReportCriterion):
    description = "Проверка наличия обязательных заголовков в отчете"
    id = 'needed_headers_check'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.headers = self.file.make_chapters(self.file_type['report_type'])
        self.config = 'VKR_HEADERS' if (self.file_type['report_type'] == 'VKR') else 'LR_HEADERS'
        self.patterns = StyleCheckSettings.CONFIGS.get(self.config)[0]["headers"]

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        result_string = ''
        patterns = []
        for pattern in self.patterns:
            patterns.append({"pattern": pattern, "marker": 0})
        if not len(self.headers):
            return answer(False, "Не найдено ни одного заголовка.<br><br>Проверьте корректность использования стилей.")
        for header in self.headers:
            header_text = header["text"].lower()
            for i in range(len(patterns)):
                pattern = patterns[i]["pattern"]
                if header_text.find(pattern.lower()) >= 0:
                   patterns[i]["marker"] = 1

        for pattern in patterns:
            if not pattern["marker"]:
                result_string += '<li>' + pattern["pattern"] + '</li>'

        result_score = 0
        if len(result_string) == 0:
            result_score = 1
        if result_score:
            return answer(result_score, "Все необходимые заголовки обнаружены!")
        else:
            result_str = f'Не найдены следующие обязательные заголовки: <ul>{result_string}</ul>'
            result_str += '''
                        Если не найден существующий раздел, попробуйте сделать следующее:
                        <ul>
                            <li>Убедитесь в отсутствии опечаток и лишних пробельных символов в названии раздела;</li>
                            <li>Убедитесь в соответствии стиля заголовка требованиям к отчету по ВКР;</li>
                            <li>Убедитесь, что заголовок состоит из одного абзаца.</li>
                        '''
            return answer(result_score, result_str)