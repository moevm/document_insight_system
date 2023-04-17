from .style_check_settings import StyleCheckSettings
from ..base_check import BaseReportCriterion, answer
from ...reports.docx_uploader.style import Style


class ReportStyleCheck(BaseReportCriterion):
    # TODO: DEPRECATED
    description = "Проверка корректности форматирования текста"
    id = "style_check"

    default_key_properties = ("font_name", "alignment")

    def __init__(self, file_info, header_styles=None, target_styles=None, key_properties=None, skip_first_page=True):
        super().__init__(file_info)
        self.skip_first_page = skip_first_page
        if target_styles is None:
            self.target_styles = StyleCheckSettings.LR_MAIN_TEXT_CONFIG
        else:
            self.target_styles = target_styles
        self.target_styles = list(map(lambda elem: {
            "name": elem["name"],
            "style": self.construct_style_from_description(elem["style"])
        },
                                      self.target_styles))
        if header_styles is None:
            self.header_styles = []
            for style_dict in StyleCheckSettings.LR_CONFIG:
                header_style = {key: style_dict["style"].get(key) for key in StyleCheckSettings.PRECHECKED_PROPS}
                style = Style()
                style.__dict__.update(header_style)
                self.header_styles.append(style)
        else:
            self.header_styles = []
            for style_dict in header_styles:
                style = Style()
                style.__dict__.update(style_dict)
                self.header_styles.append(style)
        if key_properties is None:
            self.key_properties = self.default_key_properties
        else:
            self.key_properties = key_properties
        self.header_indices = set()

    def late_init(self):
        self.file.parse_effective_styles()
        indices = self.file.get_paragraph_indices_by_style(self.header_styles)
        for sublist in indices:
            self.header_indices.update(sublist)

    @staticmethod
    def construct_style_from_description(style_dict):
        style = Style()
        style.__dict__.update(style_dict)
        return style

    def get_style_by_key_property(self, value):
        for style in self.target_styles:
            if value.items() == self.get_style_properties(style['style']).items():
                return style

    def get_style_properties(self, style):
        return {key_property: getattr(style, key_property) for key_property in self.key_properties}

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

    def get_line_after_skip(self):
        text_dict = self.file.pdf_file.text_on_page
        if len(text_dict) < 2:
            return None
        for i in range(2, len(text_dict) + 1):
            lines = text_dict[i].split("\n")
            lines = list(filter(lambda line: not (line.isspace() or len(line) == 0), lines))
            if len(lines) > 0:
                return lines[0]
        return None

    def get_index_after_skip(self):
        line = self.get_line_after_skip()
        if line is None:
            return None
        for i in range(len(self.file.styled_paragraphs)):
            par = self.file.styled_paragraphs[i]
            if par["text"].startswith(line):
                return i
        return None

    def check(self):
        self.late_init()
        if not self.skip_first_page:
            base_index = 0
        else:
            base_index = self.get_index_after_skip()
        if base_index is None:
            return answer(True, "Нечего проверять: отчёт содержит не более одной непустой страницы.")
        result = True
        result_str = ""
        valid_key_properties = tuple(
            map(lambda s: self.get_style_properties(s["style"]), self.target_styles))
        for i in range(base_index, len(self.file.styled_paragraphs)):
            if i in self.header_indices:
                continue
            par = self.file.styled_paragraphs[i]
            cur_key_property = None
            for run in par["runs"]:
                cur_key_property = self.get_style_properties(run["style"])
                if cur_key_property in valid_key_properties:
                    break
            if cur_key_property not in valid_key_properties:
                result = False
                result_str += "<br>" if len(result_str) else ""
                result_str += f'{",".join([Style._friendly_property_names[key] for key in self.key_properties])} в абзаце' \
                              f' "{par["text"][:17] + "..." if len(par["text"]) > 20 else par["text"]}" ' \
                              f'не соответствует ни одному из допустимых стилей текста.'
            else:
                checked_style = self.get_style_by_key_property(cur_key_property)
                err = self.style_diff(par, checked_style["style"])
                result = result and len(err) == 0
                err = list(map(lambda msg: f'Стиль "{checked_style["name"]}": ' + msg, err))
                result_str += ("<br>".join(err) + "<br>" if len(err) else "")
        if len(result_str) == 0:
            result_str = "Форматирование текста соответствует требованиям."
        return answer(result, result_str)
