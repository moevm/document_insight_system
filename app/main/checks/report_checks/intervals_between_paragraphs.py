from ..base_check import BaseReportCriterion, answer
from .style_check_settings import StyleCheckSettings


class ReportIntervalsParagraphsCheck(BaseReportCriterion):
    label = "Проверка значений интервалов между абзацами"
    _description = "Проверяет, что интервалы между абзацами соответствуют требованиям"
    id = "report_intervals_paragraphs_check"

    def __init__(self, file_info, params=None):
        super().__init__(file_info)
        if not params:
            params = StyleCheckSettings.DEFAULT_PARAGRAPH_INTERVALS
        self.max_line_spacing = params['line_spacing']
        self.space_before = params['space_before']
        self.space_after = params['space_after']
        self.max_problematic_paragraphs = params['max_problematic_paragraphs']

    def check(self):
        try:
            problematic_paragraphs = []

            for i, paragraph in enumerate(self.file.paragraphs):
                if not paragraph.paragraph_text or "heading" in paragraph.paragraph_style_name:
                    continue

                if (
                    (
                        paragraph.paragraph_space_after is not None
                        and paragraph.paragraph_space_after != self.space_after
                    )
                    or (
                        paragraph.paragraph_space_before is not None
                        and paragraph.paragraph_space_before != self.space_before
                    )
                    or (
                        paragraph.paragraph_line_spacing is not None
                        and paragraph.paragraph_line_spacing != self.max_line_spacing
                    )
                ):
                    preview_paragraph = paragraph.paragraph_text[:40].strip()
                    problematic_paragraphs.append({"preview": preview_paragraph, "number_paragraph": i})

            if problematic_paragraphs:
                n = len(problematic_paragraphs)
                if n >= self.max_problematic_paragraphs:
                    score = 0
                else:
                    score = 1.0 - n / self.max_problematic_paragraphs

                details = "<br>".join(
                    [
                        f"абзац (до первых 40 символов): {par['preview']} - номер параграфа: {par['number_paragraph']}"
                        for par in problematic_paragraphs
                    ]
                )

                return answer(
                    score,
                    f"Абзацы в работе имеют нерекомендованные интервалы: {details}"
                    f"<br><b>Рекомендованные значения:</b> "
                    f"межстрочный = {self.max_line_spacing}, "
                    f"интервал до абзаца = {self.space_before} pt, "
                    f"интервал после абзаца = {self.space_after} pt.",
                )

            return answer(1.0, "Все абзацы имеют рекомендованные интервалы")

        except Exception as e:
            return answer(False, f"Ошибка при проверке интервалов: {str(e)}")
