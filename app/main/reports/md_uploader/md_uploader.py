import markdown #installation: pip install markdown
import re

class MdUpload:
    def __init__(self, path_to_md_file):
        self.path_to_md_file = path_to_md_file
        self.headers = []
        self.chapters = []
        self.paragraphs = []
        self.html_text = ''
        self.tables = []
        self.chapter_with_text = []

    def read_md_file(self):
        with open(self.path_to_md_file, "r", encoding="utf-8") as f:
            md_text = f.read()
            return md_text

    def get_html_from_md(self, md_text):
            self.html_text = markdown.markdown(md_text)
            self.paragraphs = self.html_text.split('\n')

    def get_headers(self):
        header_regex = "<h1>(.*?)<\/h1>"
        self.headers = re.findall(header_regex, self.html_text)

    def get_chapters(self):
        chapter_regex = "<h2>(.*?)<\/h2>"
        self.chapters = re.findall(chapter_regex, self.html_text)
    
    def get_chapter_with_text(self):
        text = self.html_text
        chapter_name = ''
        for chapter in self.chapters:
            self.split_chapter = text.split("<h2>" + chapter + "</h2>")
            self.chapter_with_text.append(chapter_name + self.split_chapter[-2])
            chapter_name = chapter
            text = self.split_chapter[-1]
        self.chapter_with_text.append(chapter_name + text)
    
    def get_tables_size(self):
        count_table_line = 0
        count_paragraph = len(self.paragraphs)
        for line in self.paragraphs:
            if "|" in line:
                count_table_line +=1
        return round(count_table_line/count_paragraph, 4)
    
    def parse_md_file(self):
        md_text = self.read_md_file()
        self.get_html_from_md(md_text)
        self.get_headers()
        self.get_chapters()
        self.get_chapter_with_text()
        self.get_tables_size()
        return f"Заголовки:\n{self.headers}\n\nГлавы:\n{self.chapters}\n\nГлавы с текстом:\n{self.chapter_with_text}\n\nДоля таблиц в тексте:\n{self.get_tables_size()}"

def main(args):
    md_file = MdUpload(args.mdfile)
    print(md_file.parse_md_file())
    
