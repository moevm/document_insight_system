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
        "short_sections_check"
    ],
    [
        "banned_words_check"
    ],
    [
        "right_words_check"
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
        "needed_headers_check",
        {
            "headers_map" : "MD_HEADERS"
        }
    ],
    [
        "report_section_component",
        {
            "headers_map" : "MD_HEADERS"
        }
    ],
    [
        "spelling_check"
    ]
]
'''
import re
import markdown
from md2pdf.core import md2pdf
import re
from ..document_uploader import DocumentUploader
from ..pdf_document.pdf_document_manager import PdfDocumentManager


class MdUploader(DocumentUploader):
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        self.headers_main = ''
        self.html_text = ''
        self.headers_page = 1
        self.str_chapters = None
        self.tree_chapters = None


    def upload(self):
        with open(self.filepath, "r", encoding="utf-8") as f:
            md_text = f.read()
            return md_text

    def parse(self, md_text):
        self.html_text = markdown.markdown(md_text)
        self.paragraphs = self.make_paragraphs(self.html_text)
        self.parse_effective_styles()
        self.pdf_filepath = self.filepath.split('.')[0]+'.pdf'
        self.pdf_file = PdfDocumentManager(self.filepath, md2pdf(self.pdf_filepath, md_file_path=self.filepath))
    
    def make_paragraphs(self, html_text):
        html_text = html_text.replace("<li>", "").replace("</li>", "").replace("</ol>", "").replace("<ol>", "")
        self.paragraphs = [paragraph for paragraph in html_text.split('\n') if paragraph.strip()]
        return self.paragraphs

    def page_counter(self): # we need this just to find a last page and make link to the literature in banned_words_in_literature 
        if not self.page_count:
            for k, v in self.pdf_file.text_on_page.items():
                line = v[:20] if len(v) > 21 else v
                self.page_count += 1
                line = ''
                lines = v.split("\n")
                for i in range(len(lines)):
                    if i > 1:
                        break
                    if i > 0:
                        line += " "
                    line += lines[i].strip()
                self.first_lines.append(line.lower())
        self.literature_page = self.page_count #for link to page with literature
        if self.page_count < 5:
            self.page_count = 5 
        return self.page_count

    def get_main_headers(self, work_type):
        if not self.headers_main:
            header_main_regex = "<h1>(.*?)<\/h1>"
            self.headers_main = re.findall(header_main_regex, self.html_text)[0]
        return self.headers_main

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
                elif '<img alt=' in paragraph['text'] and 'Рисунок' in paragraph['text']:
                    paragraph["runs"].append({"text": par, "style": "вкр_подпись для рисунков"})
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
    
    def chapters_to_str(self):
        if self.str_chapters: return self.str_chapters
        result = []
        for chapter in self.chapters:
            result.append({
                "style": chapter['style'],
                "name": re.sub(r"<[\/\w]*>", "", chapter['text']),
                "text": "".join(re.sub(r"<[\/\w]*>", "", child['text']) for child in chapter['child'])
            })
        self.str_chapters = result
        return result
    
    def build_chapter_tree(self, chapters):
        if self.tree_chapters: return self.tree_chapters
        tree = []
        stack = [tree]
        
        for chapter in chapters:
            level = int(chapter['style'].split(' ')[-1])-1
            
            while len(stack) > level:
                stack.pop()
                
            parent = stack[-1]
            new_chapter = {
                'name': chapter['name'],
                'text': chapter['text'],
                'children': []
            }
            
            parent.append(new_chapter)
            stack.append(new_chapter['children'])
            
            chapter['node'] = new_chapter
        
        self.tree_chapters = tree
        return tree
    
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
                if header_text.find('Список использованных источников'.lower()) >= 0:
                    self.literature_header = header
        return self.literature_header
    
    def find_header_page(self, work_type):
        return self.headers_page
    
    def find_literature_page(self, work_type):
        return self.literature_page

    def parse_md_file(self):
        md_text = self.upload()
        self.parse(md_text)
        self.get_main_headers(work_type="VKR")
        self.make_chapters(work_type="VKR")
        self.find_literature_vkr(work_type="VKR")
        return f"Заголовки:\n{self.headers_main}\n\nГлавы\n{self.chapters}\n\nСписок литературы:\n\n{self.literature_header}"

    def show_chapters(self, work_type):
        chapters_str = ""
        for header in self.make_chapters(work_type):
            if header["style"] == 'heading 2':
                modified_header = re.sub(r'<h2>(.*?)</h2>', r'<h6><b>\1</b></h6>', header["text"])
                chapters_str += modified_header
            elif header["style"] == 'heading 3':
                modified_header = re.sub(r'<h3>(.*?)</h3>', r'<h6>\1</h6>', header["text"])
                chapters_str += modified_header
            elif header["style"] == 'heading 4':
                modified_header = re.sub(r'<h4>(.*?)</h4>', r'<h6>\1</h6>', header["text"])
                chapters_str += modified_header
        return chapters_str


def main(args):
    md_file = MdUploader(args.mdfile)
    print(md_file.parse_md_file())


# In case of future searching of images:
    
    # from PIL import Image
    # from io import BytesIO
    # from ..docx_uploader.inline_shape import InlineShape
    
    # def find_images(self):
    #     total_height = 0
    #     images = [k['runs'][0]['text'] for k in self.styled_paragraphs if k['runs'][0]['style'] == 'рисунок']
    #     images_regex = '(https://[\S]+\.(jpg|png))+'
    #     images_links = [re.findall(images_regex, k)[0][0] for k in images if re.findall(images_regex, k)]
    #     for link in images_links:
    #         response = requests.get(link)
    #         image = Image.open(BytesIO(response.content))
    #         dpi_image = image.info.get("dpi", (72, 72))
    #         width, height = round((image.width/dpi_image[0])*2.54, 3), round((image.height/dpi_image[1])*2.54, 3)
    #         total_height += width
    #         self.inline_shapes.append((width, height))
    #     return self.inline_shapes 
