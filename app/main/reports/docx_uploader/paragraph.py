import pandas

class Paragraph:
    def __init__(
        self,
        text=None,
        paragraph_style_name=None,
        runs=None,
        alignment=None,
        left_indent=None,
        right_indent=None,
        first_line_indent=None,
        space_after=None,
        space_before=None,
        line_spacing=None,
        line_spacing_rule=None,
        keep_together=None,
        keep_with_next=None,
        page_break_before=None,
        widow_control=None
    ):
        """
        Конструктор для создания объекта Paragraph.

        Args:
            text: Текст параграфа (по умолчанию None).
            paragraph_style_name: Имя стиля параграфа (по умолчанию None).
            runs: Список runs с текстом и стилями (по умолчанию None).
            alignment: Выравнивание параграфа (по умолчанию None).
            left_indent: Отступ слева в сантиметрах (по умолчанию None).
            right_indent: Отступ справа в сантиметрах (по умолчанию None).
            first_line_indent: Отступ первой строки в сантиметрах (по умолчанию None).
            space_after: Интервал после параграфа в пунктах (по умолчанию None).
            space_before: Интервал перед параграфом в пунктах (по умолчанию None).
            line_spacing: Межстрочный интервал (по умолчанию None).
            line_spacing_rule: Правило межстрочного интервала (по умолчанию None).
            keep_together: Сохранять строки вместе (по умолчанию None).
            keep_with_next: Сохранять с следующим параграфом (по умолчанию None).
            page_break_before: Разрыв страницы перед параграфом (по умолчанию None).
            widow_control: Контроль висячих строк (по умолчанию None).
        """
        self.text = text if text is not None else ""
        self.paragraph_style_name = paragraph_style_name if paragraph_style_name is not None else "Normal"
        self.runs = runs if runs is not None else []
        self.alignment = alignment
        self.left_indent = left_indent
        self.right_indent = right_indent
        self.first_line_indent = first_line_indent
        self.space_after = space_after
        self.space_before = space_before
        self.line_spacing = line_spacing
        self.line_spacing_rule = line_spacing_rule
        self.keep_together = keep_together
        self.keep_with_next = keep_with_next
        self.page_break_before = page_break_before
        self.widow_control = widow_control
        self.modify()

    def modify(self):
        """
        Преобразует отступы из пунктов в сантиметры и интервалы в пункты, если они не None.
        """
        if self.left_indent is not None:
            self.left_indent = self.left_indent / 28.3464566929  # Конвертация пунктов в см
        if self.right_indent is not None:
            self.right_indent = self.right_indent / 28.3464566929
        if self.first_line_indent is not None:
            self.first_line_indent = self.first_line_indent / 28.3464566929
        if self.space_after is not None:
            self.space_after = self.space_after
        if self.space_before is not None:
            self.space_before = self.space_before

    @staticmethod
    def from_doc_paragraph(doc_paragraph):
        """
        Создает объект Paragraph из объекта docx.paragraphs или словаря styled_paragraphs.

        Args:
            doc_paragraph: Объект docx.paragraphs (для DocxUploader) или словарь (для LatexUploader).

        Returns:
            Paragraph: Новый объект Paragraph с заполненными полями.
        """
        from .style import Style  # Импортируем Style внутри метода для избежания циклического импорта

        if isinstance(doc_paragraph, dict):
            # Для LatexUploader: обработка словаря из styled_paragraphs
            paragraph = Paragraph(
                text=doc_paragraph.get("text", ""),
                runs=doc_paragraph.get("runs", [])
            )
            # Установка стиля на основе runs, как в оригинальном __make_tmp_paragraphs
            if paragraph.runs:
                styles = set(style for run in paragraph.runs for style in run.get("style", []))
                paragraph.paragraph_style_name = " ".join(styles) if styles else "Normal"
            return paragraph
        else:
            # Для DocxUploader: обработка объекта docx.paragraphs
            return Paragraph(
                text=doc_paragraph.text if doc_paragraph.text else "",
                paragraph_style_name=(doc_paragraph.style.name if doc_paragraph.style else "Normal"),
                runs=[{"text": run.text, "style": Style(run, doc_paragraph)}
                      for run in doc_paragraph.runs if run.text.strip()] if doc_paragraph.runs else [],
                alignment=doc_paragraph.paragraph_format.alignment,
                left_indent=(doc_paragraph.paragraph_format.left_indent
                             if doc_paragraph.paragraph_format.left_indent else None),
                right_indent=(doc_paragraph.paragraph_format.right_indent
                              if doc_paragraph.paragraph_format.right_indent else None),
                first_line_indent=(doc_paragraph.paragraph_format.first_line_indent
                                   if doc_paragraph.paragraph_format.first_line_indent else None),
                space_after=(doc_paragraph.paragraph_format.space_after
                             if doc_paragraph.paragraph_format.space_after else None),
                space_before=(doc_paragraph.paragraph_format.space_before
                              if doc_paragraph.paragraph_format.space_before else None),
                line_spacing=doc_paragraph.paragraph_format.line_spacing,
                line_spacing_rule=doc_paragraph.paragraph_format.line_spacing_rule,
                keep_together=doc_paragraph.paragraph_format.keep_together,
                keep_with_next=doc_paragraph.paragraph_format.keep_with_next,
                page_break_before=doc_paragraph.paragraph_format.page_break_before,
                widow_control=doc_paragraph.paragraph_format.widow_control
            )

    def to_string(self):
        """
        Возвращает строковое представление параграфа для метода print_info.
        """
        df = pandas.DataFrame({
            'Values': [
                self.text, self.alignment, self.left_indent, self.right_indent,
                self.first_line_indent, self.space_after, self.space_before,
                self.line_spacing, self.line_spacing_rule, self.keep_together,
                self.keep_with_next, self.page_break_before, self.widow_control
            ]
        })
        df.index = [
            'TEXT', 'ALIGNMENT', 'LEFT_INDENT', 'RIGHT_INDENT', 'FIRST_LINE_INDENT',
            'SPACE_AFTER', 'SPACE_BEFORE', 'LINE_SPACING', 'LINE_SPACING_RULE',
            'KEEP_TOGETHER', 'KEEP_WITH_NEXT', 'PAGE_BREAK_BEFORE', 'WIDOW_CONTROL'
        ]
        return df.to_string()
