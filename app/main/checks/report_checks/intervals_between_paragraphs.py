from docx.oxml.ns import qn
from docx.shared import Pt

from ..base_check import BaseReportCriterion, answer
from ...reports.docx_uploader.style import Style
from .style_check_settings import StyleCheckSettings

TWIPS_PER_POINT = 20
LINE_SPACING_UNITS_PER_LINE = 240


class ReportIntervalsParagraphsCheck(BaseReportCriterion):
    label = "Проверка значений интервалов между абзацами"
    _description = "Проверяет, что интервалы между абзацами соответствуют требованиям"
    id = "report_intervals_paragraphs_check"

    def __init__(self, file_info, params=None):
        super().__init__(file_info)
        defaults = StyleCheckSettings.DEFAULT_PARAGRAPH_INTERVALS
        params = params or {}
        self.max_line_spacing = params.get('line_spacing', defaults['line_spacing'])
        self.space_before = params.get('space_before', defaults['space_before'])
        self.space_after = params.get('space_after', defaults['space_after'])
        self.max_problematic_paragraphs = params.get('max_problematic_paragraphs', defaults['max_problematic_paragraphs'])

    def check(self):
        try:
            if self.is_markdown:
                return answer(False, "Проверка интервалов применима к отчётам DOCX.")
            
            problematic_paragraphs = []
            unknown_paragraphs = []
            paragraphs = [p for p in self.file.file.paragraphs if p.text.strip()]
            defaults = self.file.file.styles.element.xpath('./w:docDefaults/w:pPrDefault/w:pPr/w:spacing')

            def get_spacing(paragraph, name):
                path = ["paragraph_format", name]

                if name != "line_spacing":
                    path.append("pt")

                value = Style.resolve_style_hierarchy(None, paragraph, path)

                if value is not None or not defaults:
                    return value
                
                spacing = defaults[0]
                attr = {"space_before": "before", "space_after": "after", "line_spacing": "line"}[name]
                value = spacing.get(qn(f"w:{attr}"))

                if value is None:
                    return None
                
                value = int(value)

                if name == "line_spacing":
                    line_rule = spacing.get(qn("w:lineRule"), "auto")

                    if line_rule == "auto":
                        return value / LINE_SPACING_UNITS_PER_LINE
                    else:
                        return Pt(value / TWIPS_PER_POINT)
                
                return value / TWIPS_PER_POINT

            for i, paragraph in enumerate(paragraphs):
                lower_name = paragraph.style.name.lower()
                if "heading" in lower_name or "заголовок" in lower_name:
                    continue

                values = (get_spacing(paragraph, "space_after"), get_spacing(paragraph, "space_before"), get_spacing(paragraph, "line_spacing"))
                expected = (self.space_after, self.space_before, self.max_line_spacing)
                if any(value is not None and value != target for value, target in zip(values, expected)):
                    preview_paragraph = paragraph.text[:40].strip()
                    problematic_paragraphs.append({"preview": preview_paragraph, "number_paragraph": i})
                if any(value is None for value in values):
                    unknown_paragraphs.append(i)

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

                unknown_message = (f"<br>Не удалось определить все интервалы для абзацев: {unknown_paragraphs}."
                                   if unknown_paragraphs else "")
                return answer(
                    score,
                    f"Абзацы в работе имеют нерекомендованные интервалы: {details}"
                    f"<br><b>Рекомендованные значения:</b> "
                    f"межстрочный = {self.max_line_spacing}, "
                    f"интервал до абзаца = {self.space_before} pt, "
                    f"интервал после абзаца = {self.space_after} pt." + unknown_message,
                )

            if unknown_paragraphs:
                return answer(False, f"Не удалось определить все интервалы для абзацев: {unknown_paragraphs}.")
            return answer(1.0, "Все абзацы имеют рекомендованные интервалы")

        except Exception as e:
            return answer(False, f"Ошибка при проверке интервалов: {str(e)}")
