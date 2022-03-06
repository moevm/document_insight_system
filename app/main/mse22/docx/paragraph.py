class Paragraph:

    def __init__(self, paragraph):
        self.paragraph_text = paragraph.text
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

    def print_info(self):
        print('TEXT: ', self.paragraph_text)
        print('ALIGNMENT: ', self.paragraph_alignment)
        print('LEFT_INDENT: ', self.paragraph_left_indent)
        print('RIGHT_INDENT: ', self.paragraph_right_indent)
        print('FIRST_LINE_INDENT: ', self.paragraph_first_line_indent)
        print('SPACE_AFTER: ', self.paragraph_space_after)
        print('SPACE_BEFORE: ', self.paragraph_space_before)
        print('LINE_SPACING: ', self.paragraph_line_spacing)
        print('LINE_SPACING_RULE: ', self.paragraph_line_spacing_rule)
        print('KEEP_TOGETHER: ', self.paragraph_keep_together)
        print('KEEP_WITH_NEXT: ', self.paragraph_keep_with_next)
        print('PAGE_BREAK_BEFORE: ', self.paragraph_page_break_before)
        print('WIDOW_CONTROL: ', self.paragraph_widow_control)
        print()

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
