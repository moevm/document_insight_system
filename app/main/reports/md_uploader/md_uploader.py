'''Available checks for md-file:
pack "BaseReportCriterionPackMd"

[
    [
        "simple_check"
    ],
    [
        "banned_words_in_literature"
    ],
    [
        "page_counter"
    ],
    [
        "short_sections_check"
    ],
    [
        "banned_words_check"
    ],
    [
        "right_words_check"
    ],
    [
        "banned_words_in_literature"
    ],
    [
        "literature_references"
    ],
    [
        "image_references"
    ],
    [
        "table_references"
    ],
    [
        "first_pages_check"
    ],
    [
        "main_character_check"
    ],
    [
        "needed_headers_check"
    ],
    [
        "report_section_component"
    ],
    [
        "spelling_check"
    ]
]
'''

import markdown #installation: pip install markdown
from md2pdf.core import md2pdf #installation: pip install md2pdf
import re
# from functools import reduce
from PIL import Image
from io import BytesIO
import requests

# from ..docx_uploader.inline_shape import InlineShape
from ..document_uploader import DocumentUploader
from ..pdf_document.pdf_document_manager import PdfDocumentManager


class MdUpload(DocumentUploader):
    def __init__(self, path_to_md_file):
        self.pdf_file = None
        self.path_to_md_file = path_to_md_file
        self.paragraphs = []
        self.headers_main = []
        self.headers = []
        self.chapters = []
        self.html_text = ''
        self.count = 0
        self.tables = []
        self.chapter_with_text = []
        self.literature_header = []
        self.headers_page = 1
        self.styled_paragraphs = []
        self.first_lines = []
        self.inline_shapes = []

    def upload(self):
        with open(self.path_to_md_file, "r", encoding="utf-8") as f:
            md_text = f.read()
            return md_text

    def parse(self, md_text):
        self.html_text = markdown.markdown(md_text)
        self.paragraphs = self.make_paragraphs(self.html_text)
        self.parse_effective_styles()
        self.pdf_filepath = self.path_to_md_file.split('.')[0]+'.pdf'
        self.pdf_file = PdfDocumentManager(self.path_to_md_file, md2pdf(self.pdf_filepath, md_file_path=self.path_to_md_file))
    
    def make_paragraphs(self, html_text):
        self.paragraphs = html_text.split('\n')
        return self.paragraphs

    def page_counter(self):
        if not self.count:
            for k, v in self.pdf_file.text_on_page.items():
                line = v[:20] if len(v) > 21 else v
                if re.search('ПРИЛОЖЕНИЕ [А-Я]', line.strip()):
                    break
                self.count += 1
                line = ''
                lines = v.split("\n")
                for i in range(len(lines)):
                    if i > 1:
                        break
                    if i > 0:
                        line += " "
                    line += lines[i].strip()
                self.first_lines.append(line.lower())
        return self.count

    def get_main_headers(self):
        header_main_regex = "<h1>(.*?)<\/h1>"
        self.headers_main = re.findall(header_main_regex, self.html_text)

    def make_headers(self, work_type):
        if not self.headers:
            if work_type == 'VKR':
                # find first pages
                headers = [
                    {"name": "Титульный лист", "marker": False, "key": "санкт-петербургский государственный",
                     "main_character": True, "page": 0},
                    {"name": "Задание на выпускную квалификационную работу", "marker": False, "key": "задание",
                     "main_character": True, "page": 0},
                    {"name": "Календарный план", "marker": False, "key": "календарный план", "main_character": True,
                     "page": 0},
                    {"name": "Реферат", "marker": False, "key": "реферат", "main_character": False,  "page": 0},
                    {"name": "Abstract", "marker": False, "key": "abstract", "main_character": False, "page": 0},
                    {"name": "Содержание", "marker": False, "key": "содержание", "main_character": False, "page": 0}]
                for page in range(1, self.count if self.page_counter() < 2 * len(headers) else 2 * len(headers)):
                    page_text = (self.pdf_file.get_text_on_page()[page].lower())
                    for i in range(len(headers)):
                        if not headers[i]["marker"]:
                            if page_text.find(headers[i]["key"]) >= 0:
                                headers[i]["marker"] = True
                                headers[i]["page"] = page
                                break
                self.headers = headers
        return self.headers

    def parse_effective_styles(self):
        for par in self.paragraphs:
            if len(par.strip()) > 0:
                paragraph = {"text": par, "runs": []}
                if '<h2>' in paragraph["text"]:
                    paragraph["runs"].append({"text": par, "style": "heading 2"})
                elif '<h3>' in paragraph["text"]:
                    paragraph["runs"].append({"text": par, "style": "heading 3"})
                elif '<h4>' in paragraph["text"]:
                    paragraph["runs"].append({"text": par, "style": "heading 4"})       
                elif 'Таблица' in paragraph["text"]:
                    if '|' in self.paragraphs[self.paragraphs.index(par)+1]:
                        paragraph['runs'].append({"text": par, "style": "вкр_подпись таблицы"})
                    else:
                        paragraph["runs"].append({"text": par, "style": 'body text'})
                elif '<img alt=' in paragraph['text']:
                    paragraph["runs"].append({"text": par, "style": "рисунок"})
                elif 'Рисунок' in paragraph["text"]:
                    if '<img alt=' in self.paragraphs[self.paragraphs.index(par)-1]:
                        paragraph['runs'].append({"text": par, "style": "вкр_подпись для рисунков"})
                    else:
                        paragraph["runs"].append({"text": par, "style": 'body text'})    
                else:
                    paragraph["runs"].append({"text": par, "style": 'body text'})           
                self.styled_paragraphs.append(paragraph)
            
        return self.styled_paragraphs  

    def make_chapters(self, work_type):
        if not self.chapters:
            if work_type == 'VKR':
                # find headers
                header_ind = -1
                par_num = 0
                head_par_ind = -1
                for par_ind in range(len(self.styled_paragraphs)):
                    
                    head_par_ind += 1

                    style_name = self.styled_paragraphs[par_ind]['runs'][0]['style']
                    print(par_ind)
                    print(style_name)
                    if "heading" in style_name:
                        header_ind += 1
                        par_num = 0
                        self.chapters.append({"style": style_name, "text": self.styled_paragraphs[par_ind]["text"].strip(),
                                                "styled_text": self.styled_paragraphs[par_ind], "number": head_par_ind,
                                                "child": []})
                    elif header_ind >= 0:
                        par_num += 1
                        self.chapters[header_ind]["child"].append(
                            {"style": style_name, "text": self.styled_paragraphs[par_ind]["text"],
                                "styled_text": self.styled_paragraphs[par_ind], "number": head_par_ind})    
        return self.chapters
    
    def find_images(self):
        total_height = 0
        images = [k['runs'][0]['text'] for k in self.styled_paragraphs if k['runs'][0]['style'] == 'рисунок']
        images_regex = '(https://[\S]+\.(jpg|png))+'
        images_links = [re.findall(images_regex, k)[0][0] for k in images if re.findall(images_regex, k)]
        for link in images_links:
            response = requests.get(link)
            image = Image.open(BytesIO(response.content))
            dpi_image = image.info.get("dpi", (72, 72))
            width, height = round((image.width/dpi_image[0])*2.54, 3), round((image.height/dpi_image[1])*2.54, 3)
            total_height += width
            self.inline_shapes.append((width, height))
        return self.inline_shapes    
    
    def get_tables_size(self):
        count_table_line = 0
        count_paragraph = len(self.paragraphs)
        for line in self.paragraphs:
            if "|" in line:
                count_table_line +=1
        return round(count_table_line/count_paragraph, 4)
    
    def find_literature_vkr(self, work_type):
        if not self.literature_header:
            for header in self.make_chapters(work_type):
                header_text = header["text"].lower()
                if header_text.find('список использованных источников') >= 0:
                    self.literature_header = header
        return self.literature_header
    
    def find_header_page(self, work_type):
        return self.headers_page

    def parse_md_file(self):
        md_text = self.upload()
        self.parse(md_text)
        self.make_headers(work_type="VKR")
        self.get_tables_size()
        self.make_chapters(work_type="VKR")
        self.find_images()
        self.find_literature_vkr(work_type="VKR")
        return f"Заголовки:\n{self.headers_main}\n\nГлавы\n{self.chapters}\n\nИзображения:\n\n{self.inline_shapes}"


def main(args):
    md_file = MdUpload(args.mdfile)
    print(md_file.parse_md_file())
