import re
from functools import reduce
from typing import List

import docx

from app.main.reports.pdf_document.pdf_document_manager import PdfDocumentManager

from .core_properties import CoreProperties
from .inline_shape import InlineShape
from .paragraph import Paragraph
from .table import Table, Cell
from .style import Style
from ..pdf_document.pdf_document_manager import PdfDocumentManager
from ...checks.report_checks.style_check_settings import StyleCheckSettings



class DocxUploader:
    def __init__(self):
        self.inline_shapes = []
        self.core_properties = None
        self.chapters = []
        self.paragraphs = []
        self.tables = []
        self.file = None
        self.styled_paragraphs = None
        self.special_paragraph_indices = {}
        self.pdf_file = None
        self.styles: List[Style] = []

    def upload(self, file):
        self.file = docx.Document(file)
        self.pdf_file = PdfDocumentManager(file)

    def parse(self):
        self.core_properties = CoreProperties(self.file)
        for i in range(len(self.file.inline_shapes)):
            self.inline_shapes.append(InlineShape(self.file.inline_shapes[i]))
        self.paragraphs = self.__make_paragraphs(self.file.paragraphs)
        self.parse_effective_styles()
        self.chapters = self.__make_chapters()
        self.tables = self.__make_table(self.file.tables)

    def __make_paragraphs(self, paragraphs):
        tmp_paragraphs = []
        for i in range(len(paragraphs)):
            tmp_paragraphs.append(Paragraph(paragraphs[i]))
        return tmp_paragraphs

    def __make_chapters(self):
        tmp_chapters = []
        cutoff_index = 0
        # Define work type
        try:
            cutoff_line = self.pdf_file.get_text_on_page()[2].split("\n")[0]
        except:
            return []
        if cutoff_line.startswith('ЗАДАНИЕ'):
            config = 'VKR_HEADERS'
            cutoff_line = self.pdf_file.get_text_on_page()[4].split("\n")[0]
        elif cutoff_line.startswith('Цель'):
            config = 'LR_HEADERS'
            return []
        else:
            return []
        presets = StyleCheckSettings.CONFIGS.get(config)
        prechecked_props_lst = StyleCheckSettings.PRECHECKED_PROPS
        for format_description in presets:
            prechecked_dict = {key: format_description["style"].get(key) for key in prechecked_props_lst}
            style = Style()
            style.__dict__.update(prechecked_dict)
            self.styles.append(style)
        while True:
            if cutoff_index >= len(self.styled_paragraphs):
                return []
            par_text = self.styled_paragraphs[cutoff_index]["runs"][0]["text"]
            if par_text.startswith(cutoff_line):
                break
            cutoff_index += 1
        indexes = self.build_hierarchy()
        i = cutoff_index
        header_num = -1
        p = []
        for j in range(len(indexes)):
            if indexes[j]["index"] < cutoff_index:
                continue
            if indexes[j]["level"] == 3 or indexes[j]["level"] == 4:
                continue
            if indexes[j]["level"] == 0:
                continue
            if indexes[j]["level"] == 1 or indexes[j]["level"] == 2:
                tmp_chapters.append({"level": indexes[j]["level"], "text": self.styled_paragraphs[i]["text"], "child": []})
                header_num += 1
                header_three_num = -1
                header_on_num = -1
                header_no_num = -1
                i += 1
                k = j + 1
                while i < indexes[k]["index"]:
                    header_on_num += 1
                    tmp_chapters[header_num]["child"].append({"level": 5, "text": self.styled_paragraphs[i]["text"], "number": header_on_num + 1})
                    i += 1
                while indexes[k]["level"] == 3 or indexes[k]["level"] == 4:
                    while indexes[k]["level"] == 3:
                        header_on_num += 1
                        tmp_chapters[header_num]["child"].append({"level": 3, "text": self.styled_paragraphs[i]["text"], "child": []})
                        header_three_num = header_on_num
                        header_no_num = -1
                        i += 1
                        k += 1
                        while i < indexes[k]["index"]:
                            header_no_num += 1
                            tmp_chapters[header_num]["child"][header_three_num]["child"].append({"level": 5, "text": self.styled_paragraphs[i]["text"], "number": header_no_num + 1})
                            i += 1
                    while indexes[k]["level"] == 4:
                        if header_three_num >= 0:
                            header_no_num += 1
                            tmp_chapters[header_num]["child"][header_three_num]["child"].append({"level": 4, "text": self.styled_paragraphs[i]["text"], "child": []})
                            header_ono_num = -1
                            i += 1
                            k += 1
                            while i < indexes[k]["index"]:
                                header_ono_num += 1
                                tmp_chapters[header_num]["child"][header_three_num]["child"][header_no_num]["child"].append({"level": 5, "text": self.styled_paragraphs[i]["text"], "number": header_ono_num + 1})
                                i += 1
                        else:
                            header_on_num += 1
                            tmp_chapters[header_num]["child"].append({"level": 4, "text": self.styled_paragraphs[i]["text"], "child": []})
                            header_no_num = -1
                            i += 1
                            k += 1
                            while i < indexes[k]["index"]:
                                header_no_num += 1
                                tmp_chapters[header_num]["child"][header_on_num]["child"].append({"level": 5, "text": self.styled_paragraphs[i]["text"], "number": header_no_num + 1})
                                i += 1
        return tmp_chapters

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

    def build_hierarchy(self):
        indices = self.get_paragraph_indices_by_style(self.styles)
        tagged_indices = [{"index": 0, "level": 0}, {"index": len(self.styled_paragraphs), "level": 0}]
        for j in range(len(indices)):
            tagged_indices.extend(list(map(lambda index: {"index": index, "level": j + 1,
                                                          "text": self.styled_paragraphs[index]["text"]}, indices[j])))
        tagged_indices.sort(key=lambda dct: dct["index"])
        return tagged_indices

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

    def unify_multiline_entities(self, first_line_regex_str):
        pattern = re.compile(first_line_regex_str)
        pars_to_delete = []
        skip_flag = False
        for i in range(len(self.styled_paragraphs)-1):
            if skip_flag:
                skip_flag = False
                continue
            par = self.styled_paragraphs[i]
            next_par = self.styled_paragraphs[i+1]
            if pattern.match(par["text"]):
                skip_flag = True
                par["text"] += ("\n" + next_par["text"])
                par["runs"].extend(next_par["runs"])
                pars_to_delete.append(next_par)
                continue
        for par in pars_to_delete:
            self.styled_paragraphs.remove(par)

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
    uploader.print_info()
    uploader.parse_effective_styles()
