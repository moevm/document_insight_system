import pymupdf

from app.utils import convert_to


class PdfDocumentManager:
    def __init__(self, path_to_file, pdf_filepath):
        if not pdf_filepath:
            self.pdf_file = pymupdf.open(convert_to(path_to_file, target_format='pdf'))
        else:
            self.pdf_file = pymupdf.open(pdf_filepath)
        self.pages = [self.pdf_file.load_page(page_num) for page_num in range(self.pdf_file.page_count)]
        self.page_count_all = self.pdf_file.page_count
        self.text_on_page = self.get_text_on_page()

    def get_text_on_page(self, start_page=None, end_page=None):
        # Public page numbers are one-based and the end is inclusive.
        start = 0 if start_page is None else max(start_page - 1, 0)
        end = len(self.pages) if end_page is None else max(end_page, 0)
        return {index + 1: self.pages[index].get_text() for index in range(start, min(end, len(self.pages)))}

    def get_image_num(self):
        return sum(len(self.pdf_file.get_page_images(index)) for index in range(len(self.pages)))

    def page_images(self, page_without_pril):
        total_height = 0
        for page_num in range(min(page_without_pril, len(self.pages))):
            page = self.pdf_file[page_num]
            images = self.pdf_file.get_page_images(page_num)
            for image in images:
                image_coord = page.get_image_bbox(image[7], transform=0)  # might be [1.0, 1.0, -1.0, -1.0]
                image_height = image_coord[3] - image_coord[1]
                if image_height > 0:
                    total_height += image_height
        return total_height

    def page_height(self, page_without_pril):
        page = self.pdf_file[0]  # get first page as a sample
        page_rect = page.rect
        height, top_margin = page_rect.height, page_rect.y0
        bottom_margin = height - page_rect.y1
        available_space = (height - top_margin - bottom_margin) * page_without_pril

        return available_space


def main(args):
    pdf_document_manager = PdfDocumentManager(args.filename)
    for k, v in pdf_document_manager.text_on_page.items():
        print(f"Страница №{k}" + '\n' + f"Текст: {v}", end='\n\n')
