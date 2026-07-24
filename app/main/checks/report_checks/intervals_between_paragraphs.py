from ..base_check import answer, BaseReportCriterion


class ReportIntervalsParagraphsCheck(BaseReportCriterion):
    label = "Проверка значений интервалов между абзацами"
    _description = "Межстрочный интервал должен быть равен 1.5, а интервал до и после абзаца сответсвенно равен 0pt"
    id = "report_intervals_paragraphs_check"

    def __init__(self, file_info, max_line_spacing=1.5, max_space=12, max_indent=1.5):
        super().__init__(file_info)
        self.max_line_spacing = max_line_spacing
        self.max_space = max_space
        self.max_indent = max_indent

    def check(self):
        try:
            problematic_paragraphs = []

            for i, paragraph in enumerate(self.file.paragraphs):
                if not paragraph.paragraph_text or "heading" in paragraph.paragraph_style_name:
                    continue

                if (
                    (paragraph.paragraph_space_after is not None and paragraph.paragraph_space_after != 0)
                    or (paragraph.paragraph_space_before is not None and paragraph.paragraph_space_before != 0)
                    or (paragraph.paragraph_line_spacing is not None and paragraph.paragraph_line_spacing != 1.5)
                ):
                    preview_paragraph = paragraph.paragraph_text[:40].strip()
                    problematic_paragraphs.append({"preview": preview_paragraph, "number_paragraph": i})

            if problematic_paragraphs:
                details = "<br>".join(
                    [
                        f"абзац (до первых 40 символов): {par['preview']} - номер параграфа: {par['number_paragraph']}"
                        for par in problematic_paragraphs
                    ]
                )

                return answer(
                    False,
                    f"Абзацы в работе имеют нерекомендованные интервалы: {details}",
                )

            return answer(True, "Все абзацы имеют рекомендованные интервалы")

        except Exception as e:
            return answer(False, f"Ошибка при проверке интервалов: {str(e)}")
