from docx.shared import Cm


class StyleInfo:
    def __init__(self, docx_paragraph_style):
        if docx_paragraph_style is not None:
            font = docx_paragraph_style.font
            self.font_name = font.name
            if font.size is not None:
                self.font_size = font.size.pt
            else:
                self.font_size = None
            self.bold = font.bold
            self.italic = font.italic
            self.all_caps = font.all_caps
            formatting = docx_paragraph_style.paragraph_format
            self.alignment = formatting.alignment
            if formatting.first_line_indent is not None:
                self.first_line_indent = Cm(formatting.first_line_indent.cm)
                self.first_line_indent = round(self.first_line_indent / 1000) * 1000
            else:
                self.first_line_indent = None
            if formatting.line_spacing is not None:
                self.line_spacing = Cm(formatting.line_spacing)
                self.line_spacing = round(self.line_spacing / 1000) * 1000
            else:
                self.line_spacing = None

    def __str__(self):
        return ("{0} font, {1} pt\nBold: {2}\nItalic: {3}\nAll caps: {4}\nAlignment:"
                + "{5}\nFirst line indent: {6}\nLine spacing: {7}") \
            .format(self.font_name,
                    self.__pretty_print(self.font_size),
                    self.bold,
                    self.italic,
                    self.all_caps,
                    self.alignment,
                    self.__pretty_print(self.first_line_indent),
                    self.__pretty_print(self.line_spacing)
                    )

    @staticmethod
    def __pretty_print(prop):
        if prop is None:
            return "<inherited>"
        return prop
