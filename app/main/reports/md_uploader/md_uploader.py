import re
from pathlib import Path
from types import SimpleNamespace

import markdown
from lxml import html

from ..document_uploader import DocumentUploader
from ..pdf_document.pdf_document_manager import PdfDocumentManager


class MdUploader(DocumentUploader):
    source_format = 'md'

    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        self.headers_main = ''
        self.html_text = ''
        self.headers_page = 1
        self.str_chapters = None
        self.tree_chapters = None

    def upload(self):
        return Path(self.filepath).read_text(encoding='utf-8')

    def parse(self, md_text):
        self.chapters = []
        self.styled_paragraphs = []
        self.tables = []
        self.page_count = 0
        self.first_lines = []
        self.literature_header = []
        self.literature_page = 0
        self.headers_main = ''
        self.str_chapters = self.tree_chapters = None
        self.html_text = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
        self.paragraphs = self.make_paragraphs(self.html_text)
        self.parse_effective_styles()
        self.pdf_filepath = str(Path(self.filepath).with_suffix('.pdf'))

        from md2pdf.core import md2pdf

        md2pdf(self.pdf_filepath, md_content=md_text, base_url=str(Path(self.filepath).resolve().parent))
        self.pdf_file = PdfDocumentManager(self.filepath, self.pdf_filepath)

    def make_paragraphs(self, html_text):
        root = html.fragment_fromstring(html_text or '<p></p>', create_parent='div')
        blocks = []
        for element in root:
            if element.tag in ('ol', 'ul'):
                blocks.extend(element.findall('li'))
            else:
                blocks.append(element)
        return [
            html.tostring(block, encoding='unicode')
            for block in blocks
            if block.text_content().strip() or block.findall('.//img')
        ]

    def page_counter(self):
        texts = self.pdf_file.get_text_on_page()
        self.page_count = len(texts)
        self.first_lines = [' '.join(text.splitlines()[:2]).strip().lower() for text in texts.values()]
        return self.page_count

    def get_main_headers(self, work_type='VKR'):
        if not self.headers_main:
            self.parse_effective_styles()
            self.headers_main = next(
                (par['text'] for par in self.styled_paragraphs if par['style_name'] == 'heading 1'), ''
            )
        return self.headers_main

    def parse_effective_styles(self):
        if self.styled_paragraphs:
            return self.styled_paragraphs
        for index, raw in enumerate(self.paragraphs):
            element = html.fragment_fromstring(raw)
            text = (' '.join(element.itertext()) if element.tag == 'table' else element.text_content()).strip()
            images = element.findall('.//img')
            if element.tag == 'img':
                images.append(element)
            if not text and images:
                text = ' '.join(image.get('alt', '') for image in images).strip()
            if re.fullmatch(r'h[1-6]', element.tag):
                style_name = f'heading {element.tag[1]}'
            elif images and re.search(r'рисунок\s+\d', text, re.I):
                style_name = 'вкр_подпись для рисунков'
            elif re.match(r'таблица\s+\d', text, re.I):
                style_name = 'вкр_подпись таблицы'
            elif element.tag == 'table':
                style_name = 'md_table'
                self.tables.append(element)
            elif element.tag == 'pre':
                style_name = 'листинг'
            else:
                style_name = 'body text'
            runs = []

            def collect(node, bold=False, runs=runs):
                bold = bold or node.tag in ('strong', 'b')
                if node.text:
                    runs.append({'text': node.text, 'style': SimpleNamespace(bold=bold)})
                for child in node:
                    collect(child, bold)
                    if child.tail:
                        runs.append({'text': child.tail, 'style': SimpleNamespace(bold=bold)})

            collect(element)
            self.styled_paragraphs.append(
                {
                    'text': text,
                    'runs': runs,
                    'style_name': style_name,
                    'is_list_item': element.tag == 'li',
                    'image_count': len(images),
                    'number': index,
                }
            )
        return self.styled_paragraphs

    def make_chapters(self, work_type='VKR'):
        if not self.chapters:
            self.parse_effective_styles()
            for index, paragraph in enumerate(self.styled_paragraphs):
                entry = {
                    'style': paragraph['style_name'],
                    'text': paragraph['text'],
                    'styled_text': paragraph,
                    'number': index,
                }
                if paragraph['style_name'].startswith('heading '):
                    self.chapters.append(dict(entry, child=[]))
                elif self.chapters:
                    self.chapters[-1]['child'].append(entry)
        return self.chapters

    def chapters_to_str(self):
        return [
            {
                'style': chapter['style'],
                'name': chapter['text'],
                'text': '\n'.join(child['text'] for child in chapter['child']),
            }
            for chapter in self.make_chapters()
        ]

    def build_chapter_tree(self, chapters):
        tree, stack = [], []
        for chapter in chapters:
            level = int(chapter['style'].split()[-1])
            while stack and stack[-1][0] >= level:
                stack.pop()
            node = {'name': chapter['name'], 'text': chapter['text'], 'children': []}
            (stack[-1][1]['children'] if stack else tree).append(node)
            chapter['node'] = node
            stack.append((level, node))
        return tree

    def get_tables_size(self):
        return sum(par['style_name'] == 'md_table' for par in self.styled_paragraphs) / max(len(self.paragraphs), 1)

    def find_literature_vkr(self, work_type='VKR'):
        return next(
            (
                chapter
                for chapter in self.make_chapters(work_type)
                if re.search(r'список\s+(?:использованных\s+)?(?:источников|литературы)', chapter['text'], re.I)
            ),
            [],
        )

    def find_header_page(self, work_type='VKR'):
        return self.headers_page

    def find_literature_page(self, work_type=None):
        header = self.find_literature_vkr(work_type or 'VKR')
        if not header:
            return 0
        return next(
            (
                number
                for number, text in self.pdf_file.get_text_on_page().items()
                if header['text'].lower() in text.lower()
            ),
            0,
        )

    def show_chapters(self, work_type='VKR'):
        from html import escape

        return '<br>'.join(escape(chapter['text']) for chapter in self.make_chapters(work_type))

    def parse_md_file(self):
        self.parse(self.upload())
        return f'Заголовки:\n{self.get_main_headers()}\n\nГлавы\n{self.make_chapters()}\n'


def main(args):
    print(MdUploader(args.mdfile).parse_md_file())
