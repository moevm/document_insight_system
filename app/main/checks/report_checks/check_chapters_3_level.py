import re

from ..base_check import BaseReportCriterion, answer


class ReportСhaptersLevel3ContentCheck(BaseReportCriterion):
    label = "Проверка содержания на наличие пунктов с превышающей глубиной"
    _description = "В содержании не должно быть пунктов глубже допустимой глубины"
    id = "report_3_level_in_content_check"

    def __init__(self, file_info, forbidden_depth=3, end_marker="ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ"):
        super().__init__(file_info)
        self.forbidden_depth = forbidden_depth
        self.end_marker = end_marker

    def check(self):
        try:
            paragraphs = self.file.paragraphs

            bool_content_find = False
            bool_end_content_find = False
            failed_str = []

            for paragraph in paragraphs:
                text_par = paragraph.paragraph_text.strip()
                style = str(paragraph.paragraph_style_name).lower()

                if "СОДЕРЖАНИЕ" in text_par.upper():
                    bool_content_find = True
                    continue

                if bool_content_find:
                    if "heading" in style:
                        bool_end_content_find = True
                        break
                    if self._is_forbidden_depth(text_par):
                        failed_str.append(text_par)

            if not bool_content_find:
                return answer(False, "Не найдено раздела 'Содержание'")

            if not bool_end_content_find:
                return answer(
                    False,
                    "Не найден конец раздела «Содержание». Конец содержания - это любой заголовок после него.",
                )

            if failed_str:
                result_str = (
                    f"<b>Найдено {len(failed_str)} пунктов глубже {self.forbidden_depth - 1}:</b>"
                    f"В содержании глубина пунктов не должна превышать {self.forbidden_depth - 1}. "
                    f"Примеры пунктов 1 глубины: 1.TEXT"
                    "                 2 глубины: 1.1.TEXT"
                    "                 3 глубины: 1.1.1.TEXT"
                    f"<br>Для прохождения критерия требуется убрать в содержании пункты у которых"
                    f"глубина превышает {self.forbidden_depth - 1}.<br>"
                )
                return answer(False, result_str)

            return answer(True, f"Все пункты содержания имеют глубину меньше {self.forbidden_depth}.")

        except Exception as e:
            return answer(False, f"Ошибка при проверке: {str(e)}")

    def _is_forbidden_depth(self, line):
        match = re.match(r"^(\d+(\.\d+)+)", line)

        if match:
            numbering = match.group(1)
            numbers_count = len(numbering.split("."))
            return numbers_count >= self.forbidden_depth

        return False
