import docx

from app.main.mse22.docx.base_uploader import BaseUploader
from app.main.mse22.docx.core_properties import CoreProperties
from app.main.mse22.docx.inline_shape import InlineShape
from app.main.mse22.docx.paragraph import Paragraph
from app.main.mse22.docx.table import Table, Cell


class DocxUploader(BaseUploader):
    def __init__(self):
        self.__inline_shapes = []
        self.__core_properties = None
        self.__paragraphs = []
        self.__tables = []

    def _upload(self, file):
        self.__file = docx.Document(file)

    def parcing(self):
        self.__core_properties = CoreProperties(self.__file)
        for i in range(len(self.__file.inline_shapes)):
            self.__inline_shapes.append(InlineShape(self.__file.inline_shapes[i]))
        self.__paragraphs = self.__make_paragraphs(self.__file.paragraphs)
        self.__tables = self.__make_table(self.__file.tables)

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
            self.__tables.append(Table(tables[i], table))
        return tables

    def upload_from_cli(self, file):
        self._upload(file=file)

    def print_info(self):
        print(self.__core_properties.to_string())
        for i in range(len(self.__paragraphs)):
            print(self.__paragraphs[i].to_string())


def main(args):
    file = args.file
    uploader = DocxUploader()
    uploader.upload_from_cli(file=file)
    uploader.parcing()
    uploader.print_info()
