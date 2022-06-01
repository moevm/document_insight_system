from app.main.mse22.pdf_document.pdf_document_manager import PdfDocumentManager


def check_page_count(path_to_file, min_pages=0, max_pages=None):
    pdf_manager = PdfDocumentManager(path_to_file)
    pages_count = pdf_manager.page_count
    
    if min_pages <= pages_count and (max_pages is None or pages_count <= max_pages):
        return True

    return False  