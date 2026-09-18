from docling.document_converter import DocumentConverter
from app.utils import convert_to

class DoclingPdfManager:
    def __init__(self, path_to_file, pdf_filepath):

        if not pdf_filepath:
            pdf_filepath = convert_to(path_to_file, target_format='pdf')

        self.converter = DocumentConverter()
        self.doc = self.converter.convert(pdf_filepath).document
        
        self.pages = self.doc.pages
        self.page_count = len(self.doc.pages)
        self.text_on_page = self._build_text_on_page()
    
    def _build_text_on_page(self):
        text_by_page = {}

        for item in self.doc.texts:
            if not item.prov:
                continue
            page_no = item.prov[0].page_no
            if page_no not in text_by_page:
                text_by_page[page_no] = []
            text_by_page[page_no].append(item.text)

        return {page: "\n".join(texts) for page, texts in text_by_page.items()}

    def get_text_on_page(self, start_page=None, end_page=None):
        start_page = start_page or 1
        end_page = end_page or (self.page_count + 1)

        result = {}
        for page_num in range(start_page, end_page):
            result[page_num] = self.text_on_page.get(page_num, "")
        return result

    def get_image_num(self):
        return len(self.doc.pictures)

    def page_images(self, page_without_pril):
        total_height = 0
        for item in self.doc.pictures:
            if not item.prov:
                continue
            for prov in item.prov:
                if prov.page_no <= page_without_pril and prov.bbox:
                    height = prov.bbox.b - prov.bbox.t
                    if height > 0:
                        total_height += height

        return total_height

    def page_height(self, page_without_pril):
        """
        Dont have bottom_margin and top_margin
        """
        first_page = self.doc.pages[1]
        page_size = first_page.page_size
        height = page_size.height

        available_space = height* page_without_pril
        return available_space

    def page_rows_text(self, page_num):
        result = []

        for item in self.doc.texts:
            if not item.prov:
                continue
            for prov in item.prov:
                if prov.page_no == page_num and prov.bbox:
                    result.append({
                        "text": item.text,
                        "x0": prov.bbox.l,
                        "y0": prov.bbox.t,
                        "x1": prov.bbox.r,
                        "y1": prov.bbox.b,
                    })
                    break

        return result