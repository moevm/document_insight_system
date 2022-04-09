from app.main.mse22.docx_uploader.docx_uploader import DocxUploader
from app.main.mse22.doc.converter import Converter


class DocParser(DocxUploader):

    def __init__(self):
        super().__init__()

    def parse(self, path_to_doc):
        conv = Converter(path_to_doc)
        path_to_docx = conv.convert()
        print(path_to_docx)
        return self._upload(path_to_docx)
        # return path_to_docx


def main(args):
    print(args.filename)
    parser = DocParser()
    parser.parse(args.filename)
    parser.parcing()
    parser.print_info()

