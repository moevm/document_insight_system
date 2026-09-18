import re

from ..base_check import BaseReportCriterion, answer


class ReportСhaptersLevel3ContentCheck(BaseReportCriterion):
    label = "Проверка содержания на наличия объктов 3 уровня"
    _description = "В содержании не должно быть объектов третьего уровня"
    id = "report_3_level_in_content_check"

    def __init__(self, file_info, forbidden_level=3, end_marker="ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ"):
        super().__init__(file_info)
        self.forbidden_level = forbidden_level
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
                    if "heading 2" in style or (self.end_marker in text_par and "heading" in style):
                        bool_end_content_find = True
                        break
                    if self._is_forbidden_level(text_par):
                        failed_str.append(text_par)

            if not bool_content_find:
                return answer(False, "Не найдено раздела 'Содержание'")

            if not bool_end_content_find:
                return answer(
                    False,
                    "Не найдено конца раздела 'СОДЕРЖАНИЕ'."
                    f"заголовок {self.end_marker} или любой заголовок второго уровня считаются\
                          концом раздела 'СОДЕРЖАНИЕ'",
                )

            if failed_str:
                result_str = (
                    f"Найдено {len(failed_str)} заголовков {self.forbidden_level} уровня и выше:<br>"
                    f"Заголовки {self.forbidden_level} уровня и выше: {'<br>  '.join(failed_str)}"
                    f"<br>Содержание должно содержать только заголовки меньше {self.forbidden_level} уровня.<br>"
                    "Пример заголовка 1 уровня: 1.TEXT"
                    "                 2 уровня: 1.1.TEXT"
                    "                 3 уровня: 1.1.1.TEXT"
                    "Аналогично для последующих уровней"
                    f"Уберите заголовки {self.forbidden_level} уровня и выше из раздела 'СОДЕРЖАНИЕ'"
                    f"заголовок {self.end_marker} или любой заголовок второго уровня считаются\
                          концом раздела 'СОДЕРЖАНИЕ'"
                )
                return answer(False, result_str)

            return answer(True, f"Все заголовки соответствуют требованиям (меньше {self.forbidden_level} уровеня)")

        except Exception as e:
            return answer(False, f"Ошибка при проверке: {str(e)}")

    def _is_forbidden_level(self, line):
        match = re.match(r"^(\d+(\.\d+)+)", line)

        if match:
            numbering = match.group(1)
            dots_count = numbering.count(".")
            return dots_count >= self.forbidden_level

        return False
