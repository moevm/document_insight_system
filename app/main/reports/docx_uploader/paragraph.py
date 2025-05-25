import pandas

class Paragraph:
    def __init__(
        self,
        paragraph_text=None,
        paragraph_style_name=None,
        paragraph_alignment=None,
        paragraph_left_indent=None,
        paragraph_right_indent=None,
        paragraph_first_line_indent=None,
        paragraph_space_after=None,
        paragraph_space_before=None,
        paragraph_line_spacing=None,
        paragraph_line_spacing_rule=None,
        paragraph_keep_together=None,
        paragraph_keep_with_next=None,
        paragraph_page_break_before=None,
        paragraph_widow_control=None
    ):
        """
        Конструктор для создания объекта Paragraph.

        Args:
            paragraph_text: Текст параграфа (по умолчанию None).
            paragraph_style_name: Имя стиля параграфа (по умолчанию None).
            paragraph_alignment: Выравнивание параграфа (по умолчанию None).
            paragraph_left_indent: Отступ слева (по умолчанию None).
            paragraph_right_indent: Отступ справа (по умолчанию None).
            paragraph_first_line_indent: Отступ первой строки (по умолчанию None).
            paragraph_space_after: Интервал после параграфа (по умолчанию None).
            paragraph_space_before: Интервал перед параграфом (по умолчанию None).
            paragraph_line_spacing: Межстрочный интервал (по умолчанию None).
            paragraph_line_spacing_rule: Правило межстрочного интервала (по умолчанию None).
            paragraph_keep_together: Сохранять строки вместе (по умолчанию None).
            paragraph_keep_with_next: Сохранять с следующим параграфом (по умолчанию None).
            paragraph_page_break_before: Разрыв страницы перед параграфом (по умолчанию None).
            paragraph_widow_control: Контроль висячих строк (по умолчанию None).
        """
        self.paragraph_text = paragraph_text if paragraph_text is not None else ""
        self.paragraph_style_name = paragraph_style_name if paragraph_style_name is not None else "Normal"
        self.paragraph_alignment = paragraph_alignment
        self.paragraph_left_indent = paragraph_left_indent
        self.paragraph_right_indent = paragraph_right_indent
        self.paragraph_first_line_indent = paragraph_first_line_indent
        self.paragraph_space_after = paragraph_space_after
        self.paragraph_space_before = paragraph_space_before
        self.paragraph_line_spacing = paragraph_line_spacing
        self.paragraph_line_spacing_rule = paragraph_line_spacing_rule
        self.paragraph_keep_together = paragraph_keep_together
        self.paragraph_keep_with_next = paragraph_keep_with_next
        self.paragraph_page_break_before = paragraph_page_break_before
        self.paragraph_widow_control = paragraph_widow_control
        self.modify()

    def modify(self):
        """
        Преобразует отступы из пунктов в сантиметры и интервалы в пункты, если они не None.
        """
        if self.paragraph_left_indent is not None:
            self.paragraph_left_indent = self.paragraph_left_indent.cm
        if self.paragraph_right_indent is not None:
            self.paragraph_right_indent = self.paragraph_right_indent.cm
        if self.paragraph_first_line_indent is not None:
            self.paragraph_first_line_indent = self.paragraph_first_line_indent.cm
        if self.paragraph_space_after is not None:
            self.paragraph_space_after = self.paragraph_space_after.pt
        if self.paragraph_space_before is not None:
            self.paragraph_space_before = self.paragraph_space_before.pt

    @staticmethod
    def from_doc_paragraph(doc_paragraph):
        """
        Создает объект Paragraph из объекта docx.paragraphs.

        Args:
            doc_paragraph: Объект docx.paragraphs (для DocxUploader) или словарь (для LatexUploader).

        Returns:
            Paragraph: Новый объект Paragraph с заполненными полями.
        """
        if isinstance(doc_paragraph, dict):
            # Для LatexUploader: обработка словаря из styled_paragraphs
            paragraph = Paragraph(
                paragraph_text=doc_paragraph.get("text", "")
            )
            # Установка стиля на основе runs, если они есть
            if doc_paragraph.get("runs"):
                styles = set(style for run in doc_paragraph.get("runs", []) for style in run.get("style", []))
                paragraph.paragraph_style_name = " ".join(styles) if styles else "Normal"
            return paragraph
        else:
            # Для DocxUploader: обработка объекта docx.paragraphs
            return Paragraph(
                paragraph_text=doc_paragraph.text if doc_paragraph.text else "",
                paragraph_style_name=(doc_paragraph.style.name if doc_paragraph.style else "Normal"),
                paragraph_alignment=doc_paragraph.paragraph_format.alignment,
                paragraph_left_indent=(doc_paragraph.paragraph_format.left_indent
                                      if doc_paragraph.paragraph_format.left_indent else None),
                paragraph_right_indent=(doc_paragraph.paragraph_format.right_indent
                                       if doc_paragraph.paragraph_format.right_indent else None),
                paragraph_first_line_indent=(doc_paragraph.paragraph_format.first_line_indent
                                            if doc_paragraph.paragraph_format.first_line_indent else None),
                paragraph_space_after=(doc_paragraph.paragraph_format.space_after
                                      if doc_paragraph.paragraph_format.space_after else None),
                paragraph_space_before=(doc_paragraph.paragraph_format.space_before
                                       if doc_paragraph.paragraph_format.space_before else None),
                paragraph_line_spacing=doc_paragraph.paragraph_format.line_spacing,
                paragraph_line_spacing_rule=doc_paragraph.paragraph_format.line_spacing_rule,
                paragraph_keep_together=doc_paragraph.paragraph_format.keep_together,
                paragraph_keep_with_next=doc_paragraph.paragraph_format.keep_with_next,
                paragraph_page_break_before=doc_paragraph.paragraph_format.page_break_before,
                paragraph_widow_control=doc_paragraph.paragraph_format.widow_control
            )

    def to_string(self):
        """
        Возвращает строковое представление параграфа для метода print_info.
        """
        df = pandas.DataFrame({
            'Values': [
                self.paragraph_text, self.paragraph_alignment, self.paragraph_left_indent,
                self.paragraph_right_indent, self.paragraph_first_line_indent,
                self.paragraph_space_after, self.paragraph_space_before,
                self.paragraph_line_spacing, self.paragraph_line_spacing_rule,
                self.paragraph_keep_together, self.paragraph_keep_with_next,
                self.paragraph_page_break_before, self.paragraph_widow_control
            ]
        })
        df.index = [
            'TEXT', 'ALIGNMENT', 'LEFT_INDENT', 'RIGHT_INDENT', 'FIRST_LINE_INDENT',
            'SPACE_AFTER', 'SPACE_BEFORE', 'LINE_SPACING', 'LINE_SPACING_RULE',
            'KEEP_TOGETHER', 'KEEP_WITH_NEXT', 'PAGE_BREAK_BEFORE', 'WIDOW_CONTROL'
        ]
        return df.to_string()
