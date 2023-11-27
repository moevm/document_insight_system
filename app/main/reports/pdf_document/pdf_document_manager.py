import pdfplumber

from app.utils import convert_to


class PdfDocumentManager:
    def __init__(self, path_to_file, pdf_filepath=''):
        if not pdf_filepath:
            self.pdf_file = pdfplumber.open(convert_to(path_to_file, target_format='pdf'))
        else:
            self.pdf_file = pdfplumber.open(pdf_filepath)
        self.pages = self.pdf_file.pages
        self.page_count = len(self.pages)
        self.text_on_page = self.get_text_on_page()
        # self.bboxes = []
        # self.only_text_on_page = {}

    def get_text_on_page(self):
        return {page + 1: self.pages[page].extract_text() for page in range(self.page_count)}

    # def get_only_text_on_page(self):
    #     if not self.only_text_on_page:
    #         only_text_on_page = {}
    #         for page in range(self.page_count):
    #             p = self.pages[page]
    #             print(p.curves + p.edges)
    #             ts = {
    #                 "vertical_strategy": "explicit",
    #                 "horizontal_strategy": "explicit",
    #                 "explicit_vertical_lines": self.curves_to_edges(p.curves + p.edges),
    #                 "explicit_horizontal_lines": self.curves_to_edges(p.curves + p.edges),
    #                 "intersection_y_tolerance": 10,
    #             }
    #             self.bboxes = [table.bbox for table in p.find_tables(table_settings=ts)]
    #             only_text_on_page.update({page + 1: p.filter(self.not_within_bboxes).extract_text()})
    #         self.only_text_on_page = only_text_on_page
    #     return self.only_text_on_page
    #
    # def curves_to_edges(self, cs):
    #     """See https://github.com/jsvine/pdfplumber/issues/127"""
    #     edges = []
    #     for c in cs:
    #         edges.append(pdfplumber.utils.rect_to_edges(c))
    #     return edges
    #
    # def not_within_bboxes(self, obj):
    #     """Check if the object is in any of the table's bbox."""
    #     def obj_in_bbox(_bbox):
    #         """See https://github.com/jsvine/pdfplumber/blob/stable/pdfplumber/table.py#L404"""
    #         v_mid = (obj["top"] + obj["bottom"]) / 2
    #         h_mid = (obj["x0"] + obj["x1"]) / 2
    #         x0, top, x1, bottom = _bbox
    #         return (h_mid >= x0) and (h_mid < x1) and (v_mid >= top) and (v_mid < bottom)
    #     return not any(obj_in_bbox(__bbox) for __bbox in self.bboxes)


def main(args):
    pdf_document_manager = PdfDocumentManager(args.filename)
    for k, v in pdf_document_manager.text_on_page.items():
        print(f"Страница №{k}" + '\n' + f"Текст: {v}", end='\n\n')
