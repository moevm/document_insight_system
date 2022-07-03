from functools import reduce

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH

from .core_properties import CoreProperties
from .inline_shape import InlineShape
from .paragraph import Paragraph
from .table import Table, Cell
from .style import Style


class DocxUploader:
    def __init__(self):
        self.inline_shapes = []
        self.core_properties = None
        self.paragraphs = []
        self.tables = []
        self.file = None
        self.styled_paragraphs = None
        self.special_paragraph_indices = {}

    def upload(self, file):
        self.file = docx.Document(file)

    def parse(self):
        self.core_properties = CoreProperties(self.file)
        for i in range(len(self.file.inline_shapes)):
            self.inline_shapes.append(InlineShape(self.file.inline_shapes[i]))
        self.paragraphs = self.__make_paragraphs(self.file.paragraphs)
        self.tables = self.__make_table(self.file.tables)

    def __make_paragraphs(self, paragraphs):
        tmp_paragraphs = []
        for i in range(len(paragraphs)):
            tmp_paragraphs.append(Paragraph(paragraphs[i]))
        return tmp_paragraphs

    def __make_table(self, tables):
        for i in range(len(tables)):
            table = []
            for j in range(len(tables[i].rows)):
                row = []
                for k in range(len(tables[i].rows[j].cells)):
                    tmp_paragraphs = self.__make_paragraphs(tables[i].rows[j].cells[k].paragraphs)
                    row.append(Cell(tables[i].rows[j].cells[k], tmp_paragraphs))
                table.append(row)
            self.tables.append(Table(tables[i], table))
        return tables

    # Parses styles once; subsequent calls have no effect, since the file itself shouldn't change
    def parse_effective_styles(self):
        if self.styled_paragraphs is not None:
            return
        self.styled_paragraphs = []
        for par in filter(lambda p: len(p.text.strip()) > 0, self.file.paragraphs):
            paragraph = {"text": par.text, "runs": []}
            for run in filter(lambda r: len(r.text.strip()) > 0, par.runs):
                paragraph["runs"].append({"text": run.text, "style": Style(run, par)})
            self.styled_paragraphs.append(paragraph)

    def get_paragraph_indices_by_style(self, style_list):
        result = []
        for template_style in style_list:
            matched_pars = []
            for i in range(len(self.styled_paragraphs)):
                par = self.styled_paragraphs[i]
                if reduce(lambda prev, run: prev and run["style"].matches(template_style), par["runs"], True):
                    matched_pars.append(i)
            result.append(matched_pars)
        return result

    # Demo; this will be moved later on
    def current_test(self):
        header1_style = Style()
        header1_style.bold = True
        header1_style.all_caps = True
        header1_style.alignment = WD_ALIGN_PARAGRAPH.CENTER
        header1_style.font_name = "Times New Roman"
        header1_style.font_size_pt = 14.0
        header1_style.first_line_indent_cm = 0.0
        header1_style.italic = False
        header2_style = Style()
        header2_style.font_name = "Times New Roman"
        header2_style.font_size_pt = 14.0
        header2_style.bold = True
        header2_style.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        header2_style.first_line_indent_cm = 1.25
        header2_style.italic = False
        for paragraph in self.styled_paragraphs:
            print('"{0}":'.format(paragraph["text"]))
            for run in paragraph["runs"]:
                print("\t\"{0}\": style={1}"
                      .format(run["text"], run["style"].__dict__))
                lst = []
                run["style"].matches(header2_style, lst)
                print("Diff with header 2:", lst)
        self.special_paragraph_indices["header"] = self.get_paragraph_indices_by_style([header1_style, header2_style])
        header_indices = self.special_paragraph_indices["header"]
        print(header_indices, "\n")
        for i in range(len(header_indices)):
            print("Header {0}:".format(i + 1))
            for index in header_indices[i]:
                print(self.styled_paragraphs[index]["text"])
            print("")

    def upload_from_cli(self, file):
        self.upload(file=file)

    def print_info(self):
        print(self.core_properties.to_string())
        for i in range(len(self.paragraphs)):
            print(self.paragraphs[i].to_string())

    def __str__(self):
        return self.core_properties.to_string() + '\n' + '\n'.join([self.paragraphs[i].to_string() for i in range(len(self.paragraphs))])


def main(args):
    file = args.file
    uploader = DocxUploader()
    uploader.upload_from_cli(file=file)
    uploader.parse()
    # uploader.print_info()
    uploader.parse_effective_styles()
    uploader.current_test()
