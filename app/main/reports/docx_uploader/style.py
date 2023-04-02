class Style:
    _friendly_property_names = {
        "font_name": "Имя шрифта",
        "font_size_pt": "Размер шрифта, пт",
        "bold": "Полужирное начертание",
        "italic": "Курсивное начертание",
        "all_caps": "Все заглавные",
        "alignment": "Выравнивание",
        "line_spacing": "Межстрочный интервал",
        "first_line_indent_cm": "Красная строка, см",
        "space_after_pt": "Отступ перед абзацем, пт",
        "space_before_pt": "Отступ после абзаца, пт"
    }

    def __init__(self, run=None, par=None):
        self.font_name = None
        self.font_size_pt = None
        self.bold = None
        self.italic = None
        self.all_caps = None
        self.alignment = None
        self.line_spacing = None
        # self.line_spacing_rule = None
        self.first_line_indent_cm = None
        self.space_after_pt = None
        self.space_before_pt = None
        if run is not None and par is not None:
            for attribute_name in dir(self):
                if attribute_name.startswith("set_") and callable(getattr(self, attribute_name)):
                    getattr(self, attribute_name)(run, par)

    @staticmethod
    def get_style_attribute(style, attr_names):
        nested_attr = style
        for attr_name in attr_names:
            if nested_attr is None:
                return None
            nested_attr = getattr(nested_attr, attr_name)
        return nested_attr

    @staticmethod
    def resolve_style_property(style, attr_names):
        cur_style = style
        while cur_style is not None:
            result = Style.get_style_attribute(cur_style, attr_names)
            if result is not None:
                return result
            cur_style = cur_style.base_style
        return None

    @staticmethod
    def resolve_style_hierarchy(run, par, attr_names):
        if run is not None:
            run_result = Style.get_style_attribute(run, attr_names)
            if run_result is not None:
                return run_result
            run_style_result = Style.resolve_style_property(run.style, attr_names)
            if run_style_result is not None:
                return run_style_result
        return Style.resolve_style_property(par.style, attr_names)

    def set_font_name(self, run, par):
        self.font_name = Style.resolve_style_hierarchy(run, par, ["font", "name"])
        # As a last resort you can try parsing XML directly: https://github.com/python-openxml/python-docx/issues/383

    def set_font_size_pt(self, run, par):
        self.font_size_pt = Style.resolve_style_hierarchy(run, par, ["font", "size", "pt"])
        if self.font_size_pt is not None:
            self.font_size_pt = round(self.font_size_pt * 100) / 100

    def set_bold(self, run, par):
        self.bold = Style.resolve_style_hierarchy(run, par, ["font", "bold"])
        if self.bold is None:
            self.bold = False

    def set_italic(self, run, par):
        self.italic = Style.resolve_style_hierarchy(run, par, ["font", "italic"])
        if self.italic is None:
            self.italic = False

    def set_all_caps(self, run, par):
        if run.text.upper() == run.text:
            self.all_caps = True
            return
        self.all_caps = Style.resolve_style_hierarchy(run, par, ["font", "all_caps"])
        if self.all_caps is None:
            self.all_caps = False

    def set_alignment(self, run, par):
        self.alignment = par.alignment
        if self.alignment is None:
            self.alignment = Style.resolve_style_hierarchy(None, par, ["paragraph_format", "alignment"])

    '''def set_line_spacing_rule(self, run, par):
        self.line_spacing_rule = Style.resolve_style_hierarchy(None, par, ["paragraph_format", "line_spacing_rule"])
        if self.line_spacing_rule is None:
            self.line_spacing_rule = WD_LINE_SPACING.SINGLE'''

    def set_line_spacing(self, run, par):
        self.line_spacing = Style.resolve_style_hierarchy(None, par, ["paragraph_format", "line_spacing"])
        if self.line_spacing is not None:
            self.line_spacing = round(self.line_spacing * 100) / 100

    def set_first_line_indent_cm(self, run, par):
        self.first_line_indent_cm = Style.resolve_style_hierarchy(None, par,
                                                                  ["paragraph_format", "first_line_indent", "cm"])
        if self.first_line_indent_cm is not None:
            self.first_line_indent_cm = round(self.first_line_indent_cm * 100) / 100

    def set_space_after_pt(self, run, par):
        self.space_after_pt = Style.resolve_style_hierarchy(None, par, ["paragraph_format", "space_after", "pt"])
        if self.space_after_pt is None:
            self.space_after_pt = 0.0
        else:
            self.space_after_pt = round(self.space_after_pt * 100) / 100

    def set_space_before_pt(self, run, par):
        self.space_before_pt = Style.resolve_style_hierarchy(None, par, ["paragraph_format", "space_before", "pt"])
        if self.space_before_pt is None:
            self.space_before_pt = 0.0
        else:
            self.space_before_pt = round(self.space_before_pt * 100) / 100

    # a.matches(b) != b.matches(a)
    # None in template_style == "any"; None in self == "not found"
    def matches(self, template_style, error_list=None):
        flag = True
        for property_name in dir(self):
            if callable(getattr(self, property_name)):
                continue
            if property_name[0] == "_":
                continue
            if getattr(template_style, property_name) is None:
                continue
            if getattr(self, property_name) != getattr(template_style, property_name):
                if error_list is None:
                    return False
                else:
                    flag = False
                    if getattr(self, property_name):
                        error_list.append("{0}: ожидалось \"{1}\", фактически \"{2}\"".format(
                            Style._friendly_property_names[property_name], getattr(template_style, property_name),
                            # "по умолчанию" if getattr(self, property_name) is None else getattr(self, property_name)
                            getattr(self, property_name)
                        ))
        return flag
