import re
from ..base_check import BaseReportCriterion, answer


class ReportСhaptersLevel3ContentCheck(BaseReportCriterion):
    label = "Проверка содержания на наличия объктов 3 уровня"
    _description = "В содержании не должно быть объектов третьего уровня"
    id = "report_3_level_in_content_check"

    def __init__(self, file_info):
        super().__init__(file_info)

    def check(self):
        try:
            paragraphs = self.file.paragraphs

            bool_content_find = False
            bool_end_content_find = False
            failed_str = []

            for paragraph in paragraphs:
                text_par = paragraph.paragraph_text.strip()

                if "СОДЕРЖАНИЕ" in text_par:
                    bool_content_find = True
                    continue

                if bool_content_find:
                    if self._is_level_3_or_higher_in_content(text_par):
                        failed_str.append(text_par)

                if "ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ" in text_par:
                    style = str(paragraph.paragraph_style_name).lower()
                    if "heading 2" in style:
                        bool_end_content_find = True
                        break

            if not bool_content_find:
                return answer(False, "Не найдено раздела 'Содержание'")

            if not bool_end_content_find:
                return answer(
                    False,
                    "Не найдено заголовка 'ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ' (заголовок второго уровня),"
                    "который должен идти сразу после раздела 'Содержание'",
                )

            if failed_str:
                result_str = (
                    f"Найдено {len(failed_str)} заголовков 3 уровня и выше:<br>"
                    f"Заголовки третьего уровня и выше: {'<br>  '.join(failed_str)}"
                    "<br>Содержание должно содержать только заголовки 1 и 2 уровня.<br>"
                )
                return answer(False, result_str)

            return answer(True, "Все заголовки соответствуют требованиям (1-2 уровень)")

        except Exception as e:
            return answer(False, f"Ошибка при проверке: {str(e)}")

    def _is_level_3_or_higher_in_content(self, line):
        match = re.match(r"^(\d+(\.\d+)+)", line)

        if match:
            numbering = match.group(1)
            dots_count = numbering.count(".")
            return dots_count >= 2

        return False
