from ..base_check import BaseReportCriterion, answer
from .style_check_settings import StyleCheckSettings


class ReportSequenceSectionsCheck(BaseReportCriterion):
    label = "Проверка последовательности разделов"
    _description = (
        "Структура работы не правильна: до раздела 'ВВЕДЕНИЕ' (заголовок второго уровня) должны быть в определенном порядке разделы:"
        "ЗАДАНИЕ"
        "календарный план"
        "РЕФЕРАТ"
        "ABSTRACT"
        "СОДЕРЖАНИЕ"
        "ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ (заголовок второго уровня)"
    )
    id = "report_sequence_sections_check"

    def __init__(self, file_info):
        super().__init__(file_info)
        self.required_sections = StyleCheckSettings.REQUIRED_SECTIONS_BEFORE_INTRO

    def check(self):
        try:
            paragraphs = self.file.paragraphs

            found_sections = []
            intro_found = False

            for paragraph in paragraphs:
                if not paragraph.paragraph_text:
                    continue

                text = paragraph.paragraph_text.strip()
                style = str(paragraph.paragraph_style_name).lower()

                if "ВВЕДЕНИЕ" in text:
                    if "heading 2" not in style:
                        return answer(
                            False,
                            "Раздел 'ВВЕДЕНИЕ' должен быть оформлен стилем 'Заголовок 2'",
                        )
                    intro_found = True
                    break

                if "ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ" in text:
                    if "heading 2" not in style:
                        return answer(
                            False,
                            "Раздел 'ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ' должен быть оформлен стилем 'Заголовок 2'",
                        )
                    found_sections.append("ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ")
                    continue

                for section in self.required_sections:
                    if section in text:
                        if "heading" in style:
                            return answer(
                                False,
                                f"Раздел '{section}' не должен быть оформлен как заголовок",
                            )
                        found_sections.append(section)
                        break

            if not intro_found:
                return answer(
                    False,
                    "Не найден раздел 'ВВЕДЕНИЕ' (должен быть заголовком второго уровня)",
                )

            if (
                " ".join(found_sections)
                != "ЗАДАНИЕ календарный план РЕФЕРАТ ABSTRACT СОДЕРЖАНИЕ ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ"
            ):
                result_str = (
                    f"Ваша структура работы не соотвествует требуемой!"
                    f"<br>Ваша структура: <br>   {'<br>'.join(found_sections)}"
                    f"<br>Требуемая структура: <br>   {'<br>'.join(self.required_sections)}"
                )
                return answer(False, result_str)

            return answer(
                True,
                "Проверка последовательности разделов до раздела 'ВВЕДЕНИЕ' пройдена",
            )

        except Exception as e:
            return answer(
                False,
                f"Ошибка про проверке последовательности разделов до раздела 'ВВЕДЕНИЕ': {str(e)}, {self.file.make_chapters(self.file_type['report_type'])}",
            )
