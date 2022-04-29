from app.main.mse22.docx_uploader.docx_uploader import DocxUploader
from app.main.mse22.converter_to_docx.converter import Converter


class ConvertedParser(DocxUploader):

    def __init__(self):
        super().__init__()

    def parse(self, path_to_file):
        return self._upload(Converter(path_to_file).convert())


def main(args):
    parser = ConvertedParser()
    parser.parse(args.filename)
    parser.parcing()
    parser.print_info()

