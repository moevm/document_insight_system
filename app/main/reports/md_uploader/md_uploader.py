import markdown #installation: pip install markdown
import re

from ..document_uploader import DocumentUploader

class MdUpload(DocumentUploader):
    def __init__(self, path_to_md_file):
        self.path_to_md_file = path_to_md_file
        self.paragraphs = []
        self.headers_main = []
        self.headers = []
        self.chapters = []
        self.html_text = ''
        self.tables = []
        self.chapter_with_text = []
        self.literature_header = []
        self.headers_page = 1
        self.styled_paragraphs = []

    def upload(self):
        with open(self.path_to_md_file, "r", encoding="utf-8") as f:
            md_text = f.read()
            return md_text

    def parse(self, md_text):
        self.html_text = markdown.markdown(md_text)
        self.paragraphs = self.make_paragraphs(self.html_text)
        self.parse_effective_styles()

    def make_paragraphs(self, html_text):
        self.paragraphs = html_text.split('\n')
        return self.paragraphs

    def page_counter(self):
        return 5

    def get_main_headers(self):
        header_main_regex = "<h1>(.*?)<\/h1>"
        self.headers_main = re.findall(header_main_regex, self.html_text)

    def make_headers(self, work_type):
        if not self.headers_page:
            headers_regex = "<h2>(.*?)<\/h2>"
            self.headers = re.findall(headers_regex, self.html_text)
            return self.headers

    def parse_effective_styles(self):
        for par in self.paragraphs:
            if len(par.strip()) > 0:
                paragraph = {"text": par, "runs": []}
                if '<h2>' not in paragraph['text'] and '<h1>' not in paragraph["text"]:
                    paragraph["runs"].append({"text": par, "style": 'body text'})
                    self.styled_paragraphs.append(paragraph)
                elif '<h2>' in paragraph["text"]:
                    paragraph["runs"].append({"text": par, "style": "heading 2"})    
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
    
    def get_tables_size(self):
        count_table_line = 0
        count_paragraph = len(self.paragraphs)
        for line in self.paragraphs:
            if "|" in line:
                count_table_line +=1
        return round(count_table_line/count_paragraph, 4)
    
    def find_literature_vkr(self, work_type):
        if not self.literature_header:
            for header in self.chapters:
                if header.lower() == "список использованных источников" or header == "список литературы":
                    self.literature_header = header
        return self.literature_header
    
    def find_header_page(self, work_type):
        return self.headers_page
    
    def late_init_vkr(self):
        self.headers = self.make_chapters(work_type='VKR')
    
    def parse_md_file(self):
        md_text = self.upload()
        self.parse(md_text)
        self.make_headers(work_type="VKR")
        self.get_tables_size()
        self.parse_effective_styles()
        self.make_chapters(work_type="VKR")
        self.late_init_vkr()
        return f"Заголовки:\n{len(self.styled_paragraphs)}\n\nГлавы:\n\n\nДоля таблиц в тексте:\n{self.get_tables_size()}\n\nParagraphs"


def main(args):
    md_file = MdUpload(args.mdfile)
    print(md_file.parse_md_file())

#     [
#     [
#         "simple_check"
#     ],
#     [
#         "banned_words_in_literature"
#     ],
#     [
#         "short_sections_check"
#     ],
#     [
#         "banned_words_check"
#     ],
#     [
#         "right_words_check"
#     ],
#     [
#         "banned_words_in_literature"
#     ],
#     [
#         "literature_references"
#     ],
#     [
#         "table_references"
#     ],
#     [
#         "main_character_check"
#     ],
#     [
#         "needed_headers_check"
#     ],
#     [
#         "header_check"
#     ],
#     [
#         "report_section_component"
#     ],
#     [
#         "main_text_check"
#     ],
#     [
#         "spelling_check"
#     ]
# ]
    
