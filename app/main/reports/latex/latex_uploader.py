from ..docx_uploader.core_properties import CoreProperties
from ..docx_uploader.inline_shape import InlineShape
from ..docx_uploader.paragraph import Paragraph
from ..docx_uploader.style import Style
from ..docx_uploader.table import Table, Cell
from ..pdf_document.pdf_document_manager import PdfDocumentManager
from ..document_uploader import DocumentUploader
from .utils import find_closing_brace

class LatexUploader(DocumentUploader):
    def __init__(self):
        """Инициализирует загрузчик LaTeX-документов."""
        super().__init__()
        self.inline_shapes = []
        self.core_properties = None
        self.headers = []
        self.headers_main = ''
        self.file_path = None
        self.latex_content = ''
        self.special_paragraph_indices = {}
        self.headers_page = 0
        self.page_count = 0

    def upload(self, file, pdf_filepath=''):
        """Загружает LaTeX-файл и инициализирует PDF-менеджер."""
        with open(file, 'r', encoding='utf-8') as f:
            self.latex_content = f.read()
        self.file_path = file
        self.pdf_file = PdfDocumentManager(file, pdf_filepath)

    def extract_preamble(self, latex_content):
        """Извлекает преамбулу документа."""
        start = latex_content.find(r'\documentclass')
        if start == -1:
            return ''
        end = latex_content.find(r'\begin{document}', start)
        return latex_content[start:end] if end != -1 else latex_content[start:]

    def remove_comments(self, text):
        """Удаляет комментарии из текста."""
        lines = text.split('\n')
        return '\n'.join(
            line[:line.find('%')].rstrip() if '%' in line else line.rstrip() 
            for line in lines
        )

    def extract_command(self, preamble, command_name):
        """Извлекает значение LaTeX-команды."""
        def skip_whitespaces(pos, text):
            while pos < len(text) and text[pos].isspace():
                pos += 1
            return pos

        command_str = f'\\{command_name}'
        start_idx = preamble.find(command_str)
        if start_idx == -1:
            return None

        pos = start_idx + len(command_str)
        pos = skip_whitespaces(pos, preamble)

        # Обработка опционального аргумента
        if pos < len(preamble) and preamble[pos] == '[':
            pos += 1
            close_pos, _ = find_closing_brace(preamble, pos, '[', ']')
            if close_pos == -1:
                return None
            pos = close_pos + 1
            pos = skip_whitespaces(pos, preamble)

        # Извлечение основного аргумента
        if pos >= len(preamble) or preamble[pos] != '{':
            return None

        pos += 1  # Пропускаем '{'
        close_pos, brace_level = find_closing_brace(preamble, pos)
        if brace_level != 0:
            return None

        return preamble[pos:close_pos].strip()

    def parse(self):
        """Основной метод парсинга документа."""
        raw_preamble = self.extract_preamble(self.latex_content)
        preamble = self.remove_comments(raw_preamble)
        
        self.core_properties = CoreProperties(
            title=self.extract_command(preamble, 'title'),
            author=self.extract_command(preamble, 'author'),
            date=self.extract_command(preamble, 'date')
        )
        
        self.paragraphs = self.__make_tmp_paragraphs()
        self.parse_effective_styles()
        self.tables = self.__make_tmp_tables()

    def __make_tmp_paragraphs(self):
        """Создаёт временные параграфы для тестирования."""
        return [Paragraph(None) for _ in range(3)]

    def __make_tmp_tables(self):
        """Создаёт временные таблицы для тестирования."""
        return [Table([Cell() for _ in range(3)])]

    def parse_effective_styles(self):
        """Заглушка для парсинга стилей."""
        if not hasattr(self, 'styled_paragraphs'):
            self.styled_paragraphs = [{
                "text": "Пример текста",
                "runs": []
            }]

    def upload_from_cli(self, file):
        """Интерфейс для командной строки."""
        self.upload(file=file)
    
    @staticmethod
    def main(args):
        """Точка входа CLI."""
        uploader = LatexUploader()
        uploader.upload_from_cli(file=args.file)
        uploader.parse()
        uploader.print_info()
