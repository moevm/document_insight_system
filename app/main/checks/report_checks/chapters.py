import re

from .style_check_settings import StyleCheckSettings
from ..base_check import BaseReportCriterion, answer
from ...reports.docx_uploader.style import Style


class ReportChapters(BaseReportCriterion):
    description = "Проверка оформления заголовков отчета"
    id = 'header_check'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.headers = []
        self.target_styles = StyleCheckSettings.VKR_CONFIG
        self.target_styles = list(map(lambda elem: {
            "style": self.construct_style_from_description(elem["style"])
        }, self.target_styles))
        self.docx_styles = {}
        self.style_regex = {}
        self.config = 'VKR_HEADERS' if (self.file_type['report_type'] == 'VKR') else 'LR_HEADERS'
        self.presets = StyleCheckSettings.CONFIGS.get(self.config)
        level = 0
        for format_description in self.presets:
            self.docx_styles.update({level: format_description["docx_style"]})
            pattern = re.compile(format_description["regex"])
            self.style_regex.update({level: pattern})
            level += 1

    def late_init(self):
        self.headers = self.file.make_chapters(self.file_type['report_type'])

    @staticmethod
    def construct_style_from_description(style_dict):
        style = Style()
        style.__dict__.update(style_dict)
        return style

    @staticmethod
    def style_diff(par, template_style):
        err = []
        for run in par["runs"]:
            diff_lst = []
            run["style"].matches(template_style, diff_lst)
            diff_lst = list(map(
                lambda diff: f"Заголовок \"{par['text']}\""
                             f", фрагмент "
                             f"\"{run['text']}\": {diff}.",
                diff_lst
            ))
            err.extend(diff_lst)
        return err

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        self.late_init()
        result_str = ''
        if self.file_type['report_type'] == 'VKR':
            if not len(self.headers):
                return answer(False, "Не найдено ни одного заголовка.<br><br>Проверьте корректность использования стилей.")
            for header in self.headers:
                marked_style = 0
                for key in self.docx_styles.keys():
                    if not marked_style:
                        for style_name in self.docx_styles[key]:
                            if header["style"].find(style_name) >= 0:
                                if self.style_regex[key].match(header["text"]):
                                    marked_style = 1
                                    err = self.style_diff(header["styled_text"], self.target_styles[key]["style"])
                                    err = list(map(lambda msg: f'Стиль "{header["style"]}": ' + msg, err))
                                    result_str += ("<br>".join(err) + "<br>" if len(err) else "")
                                    break
                if not marked_style:
                    err = f"Заголовок \"{header['text']}\": "
                    err += f'Стиль "{header["style"]}" не соответстует ни одному из стилей заголовков.'
                    result_str += (str(err) + "<br>")

            if not result_str:
                return answer(True, "Форматирование заголовков соответствует требованиям.")
            else:
                result_string = f'Найдены ошибки в оформлении заголовков:<br>{result_str}<br>'
                result_string += '''
                                        Попробуйте сделать следующее:
                                        <ul>
                                            <li>Убедитесь в соответствии стиля заголовка требованиям к отчету по ВКР;</li>
                                            <li>Убедитесь, что названия разделов и нумированные разделы оформлены по ГОСТу;</li>
                                            <li>Убедитесь, что красная строка не сделана с помощью пробелов или табуляции.</li>
                                        </ul>
                                        '''
                return answer(False, result_string)
        else:
            return answer(False, 'Во время обработки произошла критическая ошибка')
