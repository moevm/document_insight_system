from typing import List

from ..base_check import BaseReportCriterion, answer
from .style_check_settings import StyleCheckSettings
from ...reports.docx_uploader.style import Style

class ReportHeaders(BaseReportCriterion):
    description = "Проверка оформления заголовков отчета"
    id = 'header_check'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.headers = self.file.make_chapters(self.file_type['report_type'])
        self.errors = [": заголовок оформлен не по ГОСТу, текущий стиль: ",
                       ": заголовок имеет форматирование названия раздела(заголовок второго уровня), а его стиль: ",
                       ": Ошибка содержания заголовка, стиль которого: "]
        self.preset = 'VKR_HEADERS' if (self.file_type['report_type'] == 'VKR') else 'LR_HEADERS'
        self.styles: List[Style] = []
        presets = StyleCheckSettings.CONFIGS.get(self.preset)
        prechecked_props_lst = StyleCheckSettings.PRECHECKED_PROPS
        for format_description in presets:
            prechecked_dict = {key: format_description["style"].get(key) for key in prechecked_props_lst}
            style = Style()
            style.__dict__.update(prechecked_dict)
            self.styles.append(style)

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        err = []
        if self.file_type['report_type'] == 'VKR':
            indexes = self.file.build_vkr_hierarchy(self.styles)
            if not len(self.headers):
                return answer(False, "Не найдено ни одного заголовка.<br><br>Проверьте корректность использования стилей.")
            if len(indexes) <= 2:
                return answer(False, "Не найдено ни одного правильно оформленного заголовка.<br><br>Стандарты оформления можно найти по ссылке: ...")
            for header in self.headers:
                for index in indexes:
                    if index["index"] > header["number"]:
                        err.append({"text": header["text"], "style": header["style"], "type": 0})
                        break
                    elif index["index"] == header["number"]:
                        if index["level"] == 1:
                            if header["style"] == 'heading 2':
                                break
                            else:
                                err.append({"text": header["text"], "style": header["style"], "type": 1})
                                break
                        if index["level"] == 2:
                            if index["text"]:
                                break
                            else:
                                err.append({"text": header["text"], "style": header["style"], "type": 2})
                                break
        else:
            return answer(False, 'Во время обработки произошла критическая ошибка')

        result_score = 0
        if len(err) == 0:
            result_score = 1
        if result_score:
            return answer(result_score, "Все заголовки оформлены верно!")
        else:
            result_string = '</li><li>'.join([(k["text"] + self.errors[k["type"]] + 'Заголвок ' + k["style"].split('heading ')[1]) for k in err])
            result_str = f'Найдены ошибки в оформлении заголовков: <ul><li>{result_string}</ul>'
            result_str += '''
                        Попробуйте сделать следующее:
                        <ul>
                            <li>Убедитесь в соответствии стиля заголовка требованиям к отчету по ВКР;</li>
                            <li>Убедитесь, что названия разделов и нумированные разделы оформлены по ГОСТу;</li>
                            <li>Убедитесь, что красная строка не сделана с помощью пробелов или табуляции.</li>
                        </ul>
                        ГОСТы для стилей можно найти по ссылке: ...
                        '''
        return answer(result_score, result_str)

