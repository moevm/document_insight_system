import pdfplumber

from ..oldConverter import Converter

class PdfDocumentManager:
    def __init__(self, path_to_file):
        self.converted_name = Converter(path_to_file).convert_to_pdf()
        self.pdf_file = pdfplumber.open(self.converted_name)
        self.pages = self.pdf_file.pages
        self.page_count = len(self.pages)
        self.text_on_page = self.get_text_on_page()

    def get_text_on_page(self):
        return {page + 1: self.pages[page].extract_text() for page in range(self.page_count)}


def main(args):
    pdf_document_manager = PdfDocumentManager(args.filename)
    for k, v in pdf_document_manager.text_on_page.items():
        print(f"Страница №{k}" + '\n' + f"Текст: {v}", end='\n\n')
