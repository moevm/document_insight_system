import markdown
import re

class MdParser:
    def __init__(self):
        self.path_to_md_file = '/home/marina/src/2/mse_auto_checking_slides_vaganov/app/main/reports/md_parser/example.md'
        self.headers = []
        self.chapters = []
        self.paragraphs = []
        self.html_text = ''
        self.tables = []
        self.chapter_with_text = []
        self.literature_header = []
        self.headers_page = 0

    def get_html_from_md(self):
        with open(self.path_to_md_file, "r", encoding="utf-8") as f:
            text = f.read()
            self.html_text = markdown.markdown(text)
            self.paragraphs = self.html_text.split('\n')
            return(self.paragraphs, self.html_text)

    def get_headers(self):
        header_regex = "<h1>(.*?)<\/h1>"
        self.headers = re.findall(header_regex, self.html_text)
        return self.headers

    def get_chapters(self):
        chapter_regex = "<h2>(.*?)<\/h2>"
        self.chapters = re.findall(chapter_regex, self.html_text)
        return(self.chapters)
    
    def get_chapter_with_text(self):
        text = self.html_text
        chapter_name = ''
        for chapter in self.chapters:
            self.split_chapter = text.split("<h2>" + chapter + "</h2>")
            self.chapter_with_text.append(chapter_name + self.split_chapter[-2])
            chapter_name = chapter
            text = self.split_chapter[-1]
            if chapter == self.chapters[len(self.chapters)-1]:
                self.chapter_with_text.append(chapter_name + text)
        return self.chapter_with_text
    
    def get_tables_size(self):
        count_table_line = 0
        count_paragraph = len(self.paragraphs)
        for line in self.paragraphs:
            if "|" in line:
                count_table_line +=1
        return (count_table_line, count_table_line/count_paragraph)    


            
file = MdParser()
file.get_html_from_md()
# print(file.get_headers())
# print(file.get_chapters())
# print(file.get_chapter_with_text())
print(file.get_tables_size())

# if __name__ == '__main__':e
#     get_html_from_md()

