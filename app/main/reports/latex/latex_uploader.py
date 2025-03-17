# app/main/reports/latex/latex_uploader.py

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
        self.core_properties = None  # Хранит метаданные документа (название, автор, дата)
        self.headers = []
        self.headers_main = ''
        self.file_path = None  # Путь к загруженному файлу
        self.latex_content = ''  # Содержимое LaTeX-документа
        self.special_paragraph_indices = {}
        self.headers_page = 0
        self.page_count = 0

    def upload(self, file, pdf_filepath=''):
        with open(file, 'r', encoding='utf-8') as f:
            self.latex_content = f.read()  # Читаем содержимое файла
        self.file_path = file
        self.pdf_file = PdfDocumentManager(file, pdf_filepath)

    def extract_preamble(self, latex_content):
        """
        Извлекает преамбулу LaTeX-документа (часть между \documentclass и \begin{document}).
        :param latex_content: Содержимое LaTeX-документа.
        :return: Преамбула документа или пустая строка, если преамбула не найдена.
        """
        start = latex_content.find(r'\documentclass')  # Ищем начало преамбулы
        if start == -1:
            return ''  # Если преамбула не найдена, возвращаем пустую строку
        end = latex_content.find(r'\begin{document}', start)  # Ищем конец преамбулы
        return latex_content[start:end] if end != -1 else latex_content[start:]  # Возвращаем преамбулу

    def remove_comments(self, text):
        """
        Удаляет комментарии из текста (всё, что после символа %).
        :param text: Текст для очистки.
        :return: Текст без комментариев.
        """
        lines = text.split('\n')  # Разделяем текст на строки
        cleaned_lines = []
        for line in lines:
            comment_pos = line.find('%')  # Ищем символ комментария
            if comment_pos != -1:
                cleaned_line = line[:comment_pos].rstrip()  # Удаляем всё после символа %
            else:
                cleaned_line = line.rstrip()  # Оставляем строку без изменений
            cleaned_lines.append(cleaned_line)
        return '\n'.join(cleaned_lines)  # Собираем строки обратно в текст

    def extract_command(self, preamble, command_name):
        """
        Извлекает значение команды LaTeX (например, \title{...}).
        :param preamble: Преамбула документа.
        :param command_name: Название команды (например, 'title', 'author', 'date').
        :return: Значение команды или None, если команда не найдена.
        """
        command_str = f'\\{command_name}'  # Формируем строку команды (например, \title)
        start_idx = preamble.find(command_str)  # Ищем начало команды
        if start_idx == -1:
            return None  # Если команда не найдена, возвращаем None
        pos = start_idx + len(command_str)
        # Пропускаем пробелы после команды
        while pos < len(preamble) and preamble[pos].isspace():
            pos += 1
        # Обрабатываем опциональные аргументы (например, \title[short]{long})
        if pos < len(preamble) and preamble[pos] == '[':
            pos += 1
            bracket_level = 1
            while pos < len(preamble) and bracket_level > 0:
                if preamble[pos] == '[':
                    bracket_level += 1
                elif preamble[pos] == ']':
                    bracket_level -= 1
                pos += 1
            # Пропускаем пробелы после опционального аргумента
            while pos < len(preamble) and preamble[pos].isspace():
                pos += 1
        # Проверяем, есть ли обязательный аргумент в фигурных скобках
        if pos >= len(preamble) or preamble[pos] != '{':
            return None
        pos += 1
        start_content = pos
        brace_level = 1
        # Ищем конец аргумента, учитывая вложенные скобки
        while pos < len(preamble) and brace_level > 0:
            if preamble[pos] == '{':
                brace_level += 1
            elif preamble[pos] == '}':
                brace_level -= 1
            pos += 1
        if brace_level != 0:
            return None  # Если скобки не сбалансированы, возвращаем None
        end_content = pos - 1
        return preamble[start_content:end_content].strip()  # Возвращаем значение команды

    def parse(self):
        raw_preamble = self.extract_preamble(self.latex_content)  # Извлекаем преамбулу
        preamble = self.remove_comments(raw_preamble)  # Удаляем комментарии
        # Извлекаем метаданные
        title = self.extract_command(preamble, 'title')
        author = self.extract_command(preamble, 'author')
        date = self.extract_command(preamble, 'date')
        # Сохраняем метаданные в объект CoreProperties
        self.core_properties = CoreProperties(title=title, author=author, date=date)
        # Заглушки для остальных данных
        self.paragraphs = self.__make_paragraphs([])
        self.parse_effective_styles()
        self.tables = self.__make_table([])

    def __make_paragraphs(self, paragraphs):
        tmp_paragraphs = []
        for i in range(3):
            tmp_paragraphs.append(Paragraph(None))  # Создаем заглушку для параграфа
        return tmp_paragraph

    def parse_effective_styles(self):
         # Заглушка для парсинга стилей
        if self.styled_paragraphs:
            return
        self.styled_paragraphs = [{"text": "Пример текста", "runs": []}]    # Статические данные

    def upload_from_cli(self, file):
        self.upload(file=file)
    
    def main(args):
        file = args.file
        uploader = LatexUploader()
        uploader.upload_from_cli(file=file)
        uploader.parse()
        uploader.print_info()
