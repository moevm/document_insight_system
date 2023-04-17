import pandas


class Paragraph:

    def __init__(self, paragraph):
        self.paragraph_text = paragraph.text
        self.paragraph_style_name = paragraph.style.name
        self.paragraph_alignment = paragraph.paragraph_format.alignment
        self.paragraph_left_indent = paragraph.paragraph_format.left_indent
        self.paragraph_right_indent = paragraph.paragraph_format.right_indent
        self.paragraph_first_line_indent = paragraph.paragraph_format.first_line_indent
        self.paragraph_space_after = paragraph.paragraph_format.space_after
        self.paragraph_space_before = paragraph.paragraph_format.space_before
        self.paragraph_line_spacing = paragraph.paragraph_format.line_spacing
        self.paragraph_line_spacing_rule = paragraph.paragraph_format.line_spacing_rule
        self.paragraph_keep_together = paragraph.paragraph_format.keep_together
        self.paragraph_keep_with_next = paragraph.paragraph_format.keep_with_next
        self.paragraph_page_break_before = paragraph.paragraph_format.page_break_before
        self.paragraph_widow_control = paragraph.paragraph_format.widow_control
        self.modify()

    def to_string(self):
        df = pandas.DataFrame({'Values': [self.paragraph_text, self.paragraph_alignment, self.paragraph_left_indent,
                                          self.paragraph_right_indent, self.paragraph_first_line_indent,
                                          self.paragraph_space_after, self.paragraph_space_before,
                                          self.paragraph_line_spacing, self.paragraph_line_spacing_rule,
                                          self.paragraph_keep_together, self.paragraph_keep_with_next,
                                          self.paragraph_page_break_before, self.paragraph_widow_control]})
        df.index = ['TEXT', 'ALIGNMENT', 'LEFT_INDENT', 'RIGHT_INDENT', 'FIRST_LINE_INDENT', 'SPACE_AFTER',
                    'SPACE_BEFORE', 'LINE_SPACING', 'LINE_SPACING_RULE', 'KEEP_TOGETHER', 'KEEP_WITH_NEXT',
                    'PAGE_BREAK_BEFORE', 'WIDOW_CONTROL']
        return df.to_string()

    def modify(self):
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
