import docx

from app.main.reports.pdf_document.pdf_document_manager import PdfDocumentManager

from .core_properties import CoreProperties
from .inline_shape import InlineShape
from .paragraph import Paragraph
from .table import Table, Cell
from ..pdf_document.pdf_document_manager import PdfDocumentManager

class DocxUploader:
    def __init__(self):
        self.inline_shapes = []
        self.core_properties = None
        self.paragraphs= []
        self.tables = []
        self.file = None
        self.pdf_file = None

    def upload(self, file):
        self.file = docx.Document(file)
        self.pdf_file = PdfDocumentManager(file)

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
    