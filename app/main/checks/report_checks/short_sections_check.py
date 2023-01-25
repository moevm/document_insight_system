import re
from typing import List, Union

from .style_check_settings import StyleCheckSettings
from ..base_check import BaseReportCriterion, answer
from ...reports.docx_uploader.style import Style


class ReportShortSectionsCheck(BaseReportCriterion):
    description = "Поиск коротких разделов в отчёте"
    id = "short_sections_check"

    default_min_len = 20

    def __init__(self, file_info, presets: str = 'LR_HEADERS',
                 prechecked_props: Union[List[str], None] = StyleCheckSettings.PRECHECKED_PROPS, min_section_len=None):
        super().__init__(file_info)
        presets = StyleCheckSettings.CONFIGS.get(presets)
        self.min_section_len = min_section_len if min_section_len is not None else self.default_min_len
        prechecked_props_lst = prechecked_props
        if prechecked_props_lst is None:
            prechecked_props_lst = StyleCheckSettings.PRECHECKED_PROPS
        self.styles: List[Style] = []
        for format_description in presets:
            prechecked_dict = {key: format_description["style"].get(key) for key in prechecked_props_lst}
            style = Style()
            style.__dict__.update(prechecked_dict)
            self.styles.append(style)

    def late_init(self):
        self.file.parse_effective_styles()
        try:
            self.cutoff_line = self.file.pdf_file.get_text_on_page()[2].split("\n")[0]
        except:
            self.cutoff_line = None
        for preset in presets:
            if preset["unify_regex"] is not None:
                self.file.unify_multiline_entities(preset["unify_regex"])

    def check(self):
        self.late_init()
        if self.cutoff_line is None:
            return answer(False, "Отчёт содержит единственную страницу или вторая страница отчёта пуста.")
        result = True
        result_str = ""
        tagged_indices = self.build_header_hierarchy()
        if len(tagged_indices) == 0:
            return answer(False, "Заголовки не найдены.")
        self.calc_length(tagged_indices)
        tagged_indices = tagged_indices[1:len(tagged_indices) - 1]
        for elem in tagged_indices:
            texts = []
            for i in range(elem["index"] + 1, elem["index"] + elem["length"]):
                texts.append(self.file.styled_paragraphs[i]["text"])
            section_text = "\n".join(texts)
            length = len(re.findall("\\w+", section_text))
            if length < self.min_section_len:
                result = False
                result_str += ("<br>" if len(result_str) else "") + \
                              f'Фрагмент "{self.file.styled_paragraphs[elem["index"]]["text"]}" ' \
                              f'похож на раздел с количеством слов' \
                              f' (не считая содержимого таблиц) {length} ' \
                              f'при минимальной рекомендуемой длине раздела в ' \
                              f'{self.min_section_len} слов.'
        if len(result_str) == 0:
            result_str = "Все разделы достигают рекомендуемой длины."
        return answer(result, result_str)

    def build_header_hierarchy(self):
        cutoff_index = 0
        while True:
            if cutoff_index >= len(self.file.styled_paragraphs):
                return []
            par_text = self.file.styled_paragraphs[cutoff_index]["text"]
            if par_text.startswith(self.cutoff_line):
                break
            cutoff_index += 1
        indices = self.file.get_paragraph_indices_by_style(self.styles)
        # discard everything from the first page
        indices = list(map(lambda lst: list(filter(lambda i: i >= cutoff_index, lst)), indices))
        tagged_indices = [{"index": 0, "level": 0}, {"index": len(self.file.styled_paragraphs), "level": 0}]
        for j in range(len(indices)):
            tagged_indices.extend(list(map(lambda index: {"index": index, "level": j + 1}, indices[j])))
        tagged_indices.sort(key=lambda dct: dct["index"])
        return tagged_indices

    @staticmethod
    def calc_length(tagged_indices):
        for i in range(1, len(tagged_indices)):
            level = tagged_indices[i]["level"]
            j = i
            highest_to_react = -1
            while True:
                j -= 1
                another_level = tagged_indices[j]["level"]
                if level > another_level:
                    break
                if level == another_level:
                    tagged_indices[j]["length"] = tagged_indices[i]["index"] - tagged_indices[j]["index"]
                    break
                if highest_to_react == -1 or another_level <= highest_to_react:
                    tagged_indices[j]["length"] = tagged_indices[i]["index"] - tagged_indices[j]["index"]
                    highest_to_react = another_level - 1
