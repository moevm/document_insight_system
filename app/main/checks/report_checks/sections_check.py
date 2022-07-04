from app.main.reports.docx_uploader.style import Style
from ..base_check import BaseReportCriterion, answer


# Do not use it to detect appendices: "ПРИЛОЖЕНИЕ Х\nНАЗВАНИЕ ПРИЛОЖЕНИЯ". Use ReportAppendixCheck for that.
class ReportSectionCheck(BaseReportCriterion):
    description = "Проверка соответствия заголовков разделов требуемым стилям"
    id = "sections_check"

    def __init__(self, file_info, header_style_dicts, header_texts, prechecked_style_props):
        super().__init__(file_info)
        self.file.parse_effective_styles()
        prechecked_style_dicts = []
        for style in header_style_dicts:
            prechecked_style = {}
            for property_name in prechecked_style_props:
                prechecked_style[property_name] = style.get(property_name, None)
            prechecked_style_dicts.append(prechecked_style)
        self.header_indices = self.file.get_paragraph_indices_by_style(list(map(
            self.construct_style_from_description, prechecked_style_dicts
        )))
        self.header_styles = list(map(self.construct_style_from_description, header_style_dicts))
        self.header_texts = header_texts

    @staticmethod
    def construct_style_from_description(dct):
        style = Style()
        style.__dict__.update(dct)
        return style

    def check(self):
        result = True
        result_str = ""
        for header_level in range(len(self.header_styles)):
            indices = self.header_indices[header_level]
            template_style = self.header_styles[header_level]
            texts = self.header_texts[header_level]
            err = self.find_and_check(indices, template_style, texts)
            result = result and (len(err) == 0)
            result_str += ("<br>".join(err) + "<br>")
        if not result:
            result_str += """Если не найден существующий раздел, попробуйте сделать следующее:
            <ul>
                <li>Убедитесь в отсутствии опечаток в названии раздела;</li>
                <li>Убедитесь в соответствии стиля заголовка требованиям вашего преподавателя;</li>
                <li>Убедитесь, что красная строка не сделана с помощью пробелов или табуляции.</li>
            </ul>
            Чтобы исправить ошибку &laquo;ожидалось "...", фактически "по умолчанию"&raquo;, попробуйте следующее:
            <ul>
                <li>Выделите нужный текст и явно примените к нему недостающее форматирование;</li>
                <li>
                    Не пользуйтесь стандартным стилем. Настройте отдельный стиль для заголовков 
                    (<a href="http://se.moevm.info/doku.php/courses:informatics:reportrules">инструкция</a>)
                    и примените его к проблемному заголовку.
                </li>
            </ul>"""
        if result:
            result_str = "Пройдена!"
        return answer(result, result_str)

    def find_and_check(self, indices, template_style, texts):
        # result = True
        errors = []
        not_found_texts = []
        last_found = -1
        texts_idx = 0
        indices_idx = 0
        while True:
            if texts_idx >= len(texts):
                break
            if indices_idx >= len(indices):
                not_found_texts.append(texts[texts_idx])
                indices_idx = last_found + 1
                texts_idx += 1
                continue
            if (self.file.styled_paragraphs[indices[indices_idx]]["text"].lower().rstrip()
                == texts[texts_idx].lower().rstrip() and hasattr(template_style,
                                                                 "all_caps") and template_style.all_caps) \
                    or self.file.styled_paragraphs[indices[indices_idx]]["text"].rstrip() == texts[texts_idx].rstrip():
                last_found = indices_idx
                par_text = self.file.styled_paragraphs[indices[indices_idx]]["text"]
                for run in self.file.styled_paragraphs[indices[indices_idx]]["runs"]:
                    diff_lst = []
                    run["style"].matches(template_style, diff_lst)
                    diff_lst = list(map(
                        lambda diff: f"Абзац \"{trim(par_text, 20)}\", фрагмент \"{trim(run['text'], 20)}\": {diff}.",
                        diff_lst
                    ))
                    errors.extend(diff_lst)
                texts_idx += 1
                indices_idx += 1
            else:
                indices_idx += 1
        for header_text in not_found_texts:
            errors.append(f"Обязательный заголовок \"{header_text}\" не найден.")
        return errors


def trim(string, length):
    return string[:length-3] + "..." if len(string) > length else string
