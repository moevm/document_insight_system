import re

from ..docx_uploader.core_properties import CoreProperties
from ..docx_uploader.inline_shape import InlineShape
from ..docx_uploader.paragraph import Paragraph
from ..docx_uploader.style import Style
from ..docx_uploader.table import Table, Cell
from ..pdf_document.pdf_document_manager import PdfDocumentManager
from ..document_uploader import DocumentUploader
from .utils import find_closing_brace
from .tokenizer import LatexTokenizer
from .tokenizer import TokenType


class LatexUploader(DocumentUploader):
    STYLE_MAP = {
        "textbf": "bold",
        "textit": "italic",
        "underline": "underline",
        "emph": "italic",
        "texttt": "monospace"
    }

    def __init__(self):
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
        with open(file, 'r', encoding='utf-8') as f:
            self.latex_content = f.read()
        self.file_path = file
        self.pdf_file = PdfDocumentManager(file, pdf_filepath)

    def extract_preamble(self, latex_content):
        start = latex_content.find(r'\documentclass')
        if start == -1:
            return ''
        end = latex_content.find(r'\begin{document}', start)
        return latex_content[start:end] if end != -1 else latex_content[start:]

    def remove_comments(self, text):
        lines = text.split('\n')
        return '\n'.join(
            line[:line.find('%')].rstrip() if '%' in line else line.rstrip()
            for line in lines
        )

    def extract_command(self, preamble, command_name):
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

        if pos < len(preamble) and preamble[pos] == '[':
            pos += 1
            close_pos, _ = find_closing_brace(preamble, pos, '[', ']')
            if close_pos == -1:
                return None
            pos = close_pos + 1
            pos = skip_whitespaces(pos, preamble)

        if pos >= len(preamble) or preamble[pos] != '{':
            return None

        pos += 1
        close_pos, brace_level = find_closing_brace(preamble, pos)
        if brace_level != 0:
            return None

        return preamble[pos:close_pos].strip()
    
    def extract_core_properties_from_preamble(self):
        preamble = self.extract_preamble(self.latex_content)
        preamble = self.remove_comments(preamble)

        title = self.extract_command(preamble, 'title')
        author = self.extract_command(preamble, 'author')
        date = self.extract_command(preamble, 'date')
        university = self.extract_command(preamble, 'university')
        faculty = self.extract_command(preamble, 'faculty')
        department = self.extract_command(preamble, 'department')
        speciality = self.extract_command(preamble, 'speciality')
        degree = self.extract_command(preamble, 'degree')

        self.core_properties = CoreProperties(
            title=title,
            author=author,
            date=date,
            university=university,
            faculty=faculty,
            department=department,
            speciality=speciality,
            degree=degree
        )

    def parse(self):
        self.extract_core_properties_from_preamble()

        tokenizer = LatexTokenizer()
        self.tokens = tokenizer.tokenize(self.latex_content)

        self._process_tokens()
        self.paragraphs = self.__make_tmp_paragraphs()
        self.parse_effective_styles()
        self.tables = self.__make_tmp_tables()

    def _process_tokens(self):
        self.env_stack = []
        for token in self.tokens:
            match token.type:
                case TokenType.COMMAND:
                    self._handle_command_token(token)
                case TokenType.ENVIRONMENT:
                    self._handle_environment_token(token)

    def _handle_command_token(self, token):
        pass

    def _handle_environment_token(self, token):
        pass 

    def __make_tmp_paragraphs(self):
        tmp_paragraphs = []
        
        for styled_par in self.styled_paragraphs:
            paragraph = Paragraph.from_doc_paragraph(styled_par)
            tmp_paragraphs.append(paragraph)
    
        return tmp_paragraphs


    def __make_tmp_tables(self):
        return [Table([Cell() for _ in range(3)])]

    def parse_effective_styles(self):
        styled_paragraphs = []
        current_paragraph = {"text": "", "runs": []}

        def apply_styles(text, styles):
            return {
                "text": text,
                "style": list(styles)
            }

        i = 0
        while i < len(self.tokens):
            token = self.tokens[i]

            match token.type:
                case TokenType.COMMAND:
                    cmd = token.value
                    if cmd not in self.STYLE_MAP:
                        i += 1
                        continue

                    if i + 2 < len(self.tokens) and self.tokens[i + 1].type == TokenType.BRACE_OPEN:
                        j = i + 2
                        text_inside = ""
                        brace_level = 1
                        while j < len(self.tokens) and brace_level > 0:
                            match self.tokens[j].type:
                                case TokenType.BRACE_OPEN:
                                    brace_level += 1
                                case TokenType.BRACE_CLOSE:
                                    brace_level -= 1
                                    if brace_level == 0:
                                        break
                                case TokenType.TEXT:
                                    text_inside += self.tokens[j].value
                            j += 1

                        style = self.STYLE_MAP[cmd]
                        current_paragraph["runs"].append(apply_styles(text_inside, [style]))
                        current_paragraph["text"] += text_inside
                        i = j
                    else:
                        i += 1

                case TokenType.TEXT:
                    current_paragraph["runs"].append(apply_styles(token.value, []))
                    current_paragraph["text"] += token.value
                    i += 1

                case TokenType.SPECIAL_CHAR:
                    current_paragraph["runs"].append(apply_styles(" ", []))
                    current_paragraph["text"] += " "
                    i += 1

                case _:
                    i += 1

        if current_paragraph["text"]:
            styled_paragraphs.append(current_paragraph)

        self.styled_paragraphs = styled_paragraphs

    def page_counter(self):
        if self.page_count:
            return self.page_count

        for k, v in self.pdf_file.text_on_page.items():
            preview = v[:20] if len(v) > 20 else v
            if re.search(r'ПРИЛОЖЕНИЕ [А-Я]', preview.strip()):
                break

            self.page_count += 1

            lines = v.split("\n")
            first_two = " ".join(line.strip() for line in lines[:2])
            self.first_lines.append(first_two.lower())

        return self.page_count

    def make_headers(self, work_type):
        if self.headers:
            return self.headers

        if work_type == 'VKR':
            headers = [
                {"name": "Титульный лист", "marker": False, "key": "санкт-петербургский государственный",
                "main_character": True, "page": 0},
                {"name": "Задание на выпускную квалификационную работу", "marker": False, "key": "задание",
                "main_character": True, "page": 0},
                {"name": "Календарный план", "marker": False, "key": "календарный план", "main_character": True,
                "page": 0},
                {"name": "Реферат", "marker": False, "key": "реферат", "main_character": False,  "page": 0},
                {"name": "Abstract", "marker": False, "key": "abstract", "main_character": False, "page": 0},
                {"name": "Cодержание", "marker": False, "key": "содержание", "main_character": False, "page": 0}
            ]

            for page in range(1, self.page_count if self.page_counter() < 2 * len(headers) else 2 * len(headers)):
                page_text = (self.pdf_file.get_text_on_page()[page].split("\n")[0]).lower()
                for i in range(len(headers)):
                    if not headers[i]["marker"]:
                        if page_text.find(headers[i]["key"]) >= 0:
                            headers[i]["marker"] = True
                            headers[i]["page"] = page
                            break

            self.headers = headers

        return self.headers

    def find_header_page(self, work_type):
        if self.headers_page:
            return self.headers_page

        if work_type != 'VKR':
            self.headers_page = 1
            return self.headers_page

        for header in self.make_headers(work_type):
            if header["name"].find('Cодержание') >= 0:
                self.headers_page = header["page"] if header["page"] else 1
                break

        return self.headers_page
    
    def make_chapters(self, work_type):
        if self.chapters:
            return self.chapters
        tmp_chapters = []
        if work_type == 'VKR':
            header_ind = -1
            par_num = 0
            head_par_ind = -1
            for par_ind in range(len(self.styled_paragraphs)):
                head_par_ind += 1
                style_name = self.paragraphs[par_ind].paragraph_style_name.lower()
                if style_name.find("heading") >= 0:
                    header_ind += 1
                    par_num = 0
                    tmp_chapters.append({"style": style_name, "text": self.styled_paragraphs[par_ind]["text"].strip(),
                                         "styled_text": self.styled_paragraphs[par_ind], "number": head_par_ind,
                                         "child": []})
                elif header_ind >= 0:
                    par_num += 1
                    tmp_chapters[header_ind]["child"].append(
                        {"style": style_name, "text": self.styled_paragraphs[par_ind]["text"],
                         "styled_text": self.styled_paragraphs[par_ind], "number": head_par_ind})
            self.chapters = tmp_chapters
        return self.chapters
    
    def find_literature_vkr(self, work_type):
        if self.literature_header:
            return self.literature_header
        for header in self.make_chapters(work_type):
            header_text = header["text"].lower()
            if header_text.find('список использованных источников') >= 0:
                self.literature_header = header
        return self.literature_header
    
    def find_literature_page(self):
        if self.literature_page:
            return self.literature_page
        
        for k, v in self.pdf_file.text_on_page.items():
            line = v[:40] if len(v) > 21 else v
            if re.search('список[ \t]*(использованных|использованной|)[ \t]*(источников|литературы)', line.strip().lower()):
                break
            self.literature_page += 1
        self.literature_page += 1

        return self.literature_page

    def show_chapters(self, work_type):
        chapters_str = "<br>"
        for header in self.make_chapters(work_type):
            if header["style"] == 'heading 2':
                chapters_str += header["text"] + "<br>"
            else:
                chapters_str += "&nbsp;&nbsp;&nbsp;&nbsp;" + header["text"] + "<br>"
        return chapters_str

    def upload_from_cli(self, file):
        self.upload(file=file)


    

    @staticmethod
    def main(args):
        uploader = LatexUploader()
        uploader.upload_from_cli(file=args.file)
        uploader.parse()
        uploader.print_info()
