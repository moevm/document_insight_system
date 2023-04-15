import re
from typing import List, Union

from app.main.reports.docx_uploader.style import Style
from .style_check_settings import StyleCheckSettings
from ..base_check import BaseReportCriterion, answer


class LRReportSectionCheck(BaseReportCriterion):
    # TODO: DEPRECATED
    description = "Проверка соответствия заголовков разделов требуемым стилям"
    id = "lr_sections_check"

    def __init__(self, file_info, presets: str = 'LR_HEADERS',
                 prechecked_props: Union[List[str], None] = StyleCheckSettings.PRECHECKED_PROPS):
        super().__init__(file_info)
        presets = StyleCheckSettings.CONFIGS.get(presets)
        if prechecked_props is None:
            self.prechecked_props = StyleCheckSettings.PRECHECKED_PROPS
        else:
            self.prechecked_props = prechecked_props
        self.presets = presets

    @staticmethod
    def construct_style_from_description(dct):
        style = Style()
        style.__dict__.update(dct)
        return style

    def check(self):
        self.file.parse_effective_styles()
        result = True
        result_str = ""
        for preset in self.presets:
            full_style = self.construct_style_from_description(preset["style"])
            precheck_dict = {key: preset["style"].get(key) for key in self.prechecked_props}
            precheck_style = self.construct_style_from_description(precheck_dict)
            err = self.check_marked_headers(preset["unify_regex"], preset["regex"],
                                            precheck_style, full_style, preset["headers"])
            result = result and (len(err) == 0)
            result_str += ("<br>".join(err) + "<br>" if len(err) else "")
        if len(result_str) == 0:
            result_str = "Пройдена!"
        else:
            result_str += '''
            Если не найден существующий раздел, попробуйте сделать следующее:
            <ul>
                <li>Убедитесь, что разделы расположены в правильном порядке;</li>
                <li>Убедитесь в отсутствии опечаток и лишних пробельных символов в названии раздела;</li>
                <li>Убедитесь в соответствии стиля заголовка требованиям вашего преподавателя;</li>
                <li>Если в требованиях к оформлению не указано, что заголовок должен занимать несколько строк,
                    убедитесь, что заголовок состоит из одного абзаца;</li>
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
            </ul>
            Ошибки вида &laquo;ошибочная маркировка разделов&raquo; часто вызваны другими ошибками; 
            их исправлять рекомендуется в последнюю очередь.
            '''
        return answer(result, result_str)

    @staticmethod
    def style_diff(par, template_style):
        err = []
        for run in par["runs"]:
            diff_lst = []
            run["style"].matches(template_style, diff_lst)
            diff_lst = list(map(
                lambda diff: f"Абзац \"{trim(par['text'], 20)}\", фрагмент \"{trim(run['text'], 20)}\": {diff}.",
                diff_lst
            ))
            err.extend(diff_lst)
        return err

    # unify_regex is used in self.file.unify_multiline_entities()
    # header_regex has two capture groups: first is marker and second is header itself (no decorations)
    def check_marked_headers(self, unify_regex, header_regex, precheck_style, template_style, headers):
        # if unify_regex is not None:
        #     self.file.unify_multiline_entities(unify_regex)
        indices = self.file.get_paragraph_indices_by_style([precheck_style])[0]
        found_texts = list(map(lambda i: self.file.styled_paragraphs[i]["text"], indices))
        pars = list(map(lambda i: self.file.styled_paragraphs[i], indices))
        pattern = re.compile(header_regex)
        errors = []
        marker_idx = 0
        header_idx = 0
        found_idx = 0
        last_found = -1
        last_punished = -1
        while True:
            if header_idx >= len(headers):
                break
            if found_idx >= len(found_texts):
                errors.append(f'Обязательный раздел "{headers[header_idx]}" не найден.')
                found_idx = last_found + 1
                marker_idx = last_found + 1
                header_idx += 1
                continue
            match = pattern.match(found_texts[found_idx])
            if match:
                if headers[header_idx].lower() in match.group(2).lower():
                    errors.extend(self.style_diff(pars[found_idx], template_style))
                    last_found = found_idx
                    marker_idx += 1
                    header_idx += 1
                    found_idx += 1
                else:
                    found_idx += 1
                    marker_idx += 1
            else:
                found_idx += 1
        return errors


def trim(string, length):
    return string[:length - 3] + "..." if len(string) > length else string
