from .core_properties import CoreProperties
from .inline_shape import InlineShape
from .paragraph import Paragraph
from .style import Style
from .table import Table, Cell
from ..pdf_document.pdf_document_manager import PdfDocumentManager
from ..document_uploader import DocumentUploader

class LatexUploader(DocumentUploader):
    def __init__(self):
        super().__init__()
        self.inline_shapes = []
        self.core_properties = None
        self.headers = []
        self.headers_main = ''
        self.file = None
        self.special_paragraph_indices = {}
        self.headers_page = 0
        self.page_count = 0

    def upload(self, file, pdf_filepath=''):
        # Заглушка для загрузки файла
        self.file = file  # В реальности здесь будет парсинг LaTeX файла
        self.pdf_file = PdfDocumentManager(file, pdf_filepath)

    def parse(self):
        # Заглушка для парсинга
        self.core_properties = CoreProperties(self.file)  # В реальности здесь будет парсинг свойств LaTeX
        self.paragraphs = self.__make_paragraphs([])  # Заглушка для параграфов
        self.parse_effective_styles()  # Заглушка для стилей
        self.tables = self.__make_table([])  # Заглушка для таблиц

    def __make_paragraphs(self, paragraphs):
        # Заглушка для создания параграфов
        tmp_paragraphs = []
        for i in range(3):  # Пример статических данных
            tmp_paragraphs.append(Paragraph(None))  # Заглушка для параграфа
        return tmp_paragraphs

    def __make_table(self, tables):
        # Заглушка для создания таблиц
        tmp_tables = []
        for i in range(2):  # Пример статических данных
            tmp_tables.append(Table(None, []))  # Заглушка для таблицы
        return tmp_tables

    def parse_effective_styles(self):
        # Заглушка для парсинга стилей
        if self.styled_paragraphs:
            return
        self.styled_paragraphs = [{"text": "Пример текста", "runs": []}]  # Статические данные

    def upload_from_cli(self, file):
        self.upload(file=file)

    # def print_info(self):
    #     print("LaTeX Uploader Info:")
    #     print("Static data for testing purposes.")

def main(args):
    file = args.file
    uploader = LatexUploader()
    uploader.upload_from_cli(file=file)
    uploader.parse()
    uploader.print_info()