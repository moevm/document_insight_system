from .style_check_settings import StyleCheckSettings
from ..base_check import BaseReportCriterion, answer
from ...reports.docx_uploader.style import Style


class ReportMainTextCheck(BaseReportCriterion):
    description = "Проверка оформления основного текста отчета"
    id = 'main_text_check'

    def __init__(self, file_info,
                 main_text_styles=["body text", "листинг", "вкр_подпись для рисунков", "вкр_подпись таблицы"],
                 main_text_styles_names=["Основной текст;ВКР_Основной текст", "ВКР_Подпись таблицы",
                                         "ВКР_Подпись для рисунков, схем", "ВКР_Содержимое таблицы"]):
        super().__init__(file_info)
        self.headers = []
        self.main_text_styles = main_text_styles
        self.main_text_styles_names = main_text_styles_names
        self.target_styles = StyleCheckSettings.VKR_MAIN_TEXT_CONFIG
        self.target_styles = list(map(lambda elem: {
            "name": elem["name"],
            "style": self.construct_style_from_description(elem["style"])
        }, self.target_styles))

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
                lambda diff: f"Абзац \"{par['text'][:17] + '...' if len(par['text']) > 20 else par['text']}\""
                             f", фрагмент "
                             f"\"{run['text'][:17] + '...' if len(run['text']) > 20 else run['text']}\": {diff}.",
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
                return answer(False,
                              "Не найдено ни одного заголовка.<br><br>Проверьте корректность использования стилей.")
            for header in self.headers:
                if header["text"].find("ПРИЛОЖЕНИЕ") >= 0:
                    break
                err_string = ''
                for child in header["child"]:
                    marked_style = 0
                    for i in range(len(self.main_text_styles)):
                        if child["style"].find(self.main_text_styles[i]) >= 0:
                            marked_style = 1
                            err = self.style_diff(child["styled_text"], self.target_styles[i]["style"])
                            err = list(map(lambda msg: f'Стиль "{child["style"]}": ' + msg, err))
                            err_string += ("<br>".join(err) + "<br>" if len(err) else "")
                            break
                    if not marked_style:
                        err = f"Абзац \"{child['text'][:17] + '...' if len(child['text']) > 20 else child['text']}\": "
                        err += f'Стиль "{child["style"]}" не соответстует ни одному из стилей основного текста.'
                        err_string += (str(err) + "<br>")
                if err_string:
                    result_str += f'<b>&nbsp;&nbsp;&nbsp;&nbsp;Ошибки в разделе {header["text"]}:</b><br>'
                    result_str += err_string
            if not result_str:
                return answer(True, "Форматирование текста соответствует требованиям.")
            else:
                result_str += f'<br><br>Перечень допустимых стилей основного текста (Названия как в документе):' \
                              f'<br><br>{"<br>".join(x for x in self.main_text_styles_names)}'
                result_str += f'<br><br>Если в вашем документе нет какого-либо из перечисленных стилей, перенесите ' \
                              f'текст пояснительной записки в документ с последней версией ' \
                              f'<a href="https://drive.google.com/file/d/1KK7fZkAl9eWNzCQlIHm6S4NynwxhkuV9/view">шаблона</a>.'
                return answer(False, result_str)
        else:
            return answer(False, 'Во время обработки произошла критическая ошибка')
