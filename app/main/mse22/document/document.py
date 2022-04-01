import docx

from app.main.mse22.document.style_info import StyleInfo
from app.main.mse22.document.page_creator import PageCreator


class Document:
    def __init__(self, docx_document, filename):
        core_props = docx_document.core_properties
        self.info = DocumentInfo(core_props.author, core_props.created, core_props.modified)
        self.pages = PageCreator().createPageObjects(filename)

    def __str__(self):
        return "document.Document object:\nPages:\n{0}\nInfo: {1}".format(self.pages, self.info)


class DocumentInfo:
    def __init__(self, author, datetime_created, datetime_modified):
        self.author = author
        self.datetime_created = datetime_created
        self.datetime_modified = datetime_modified

    def __str__(self):
        return "document.DocumentInfo object:\nAuthor: {0}\nCreated: {1}\nModified: {2}"\
            .format(self.author, self.datetime_created, self.datetime_modified)


def main(args):
    docx_document = docx.Document(args.filename)
    parsed_document = Document(docx_document, args.filename)
    print(parsed_document)
    print()
    for page in parsed_document.pages:
        print(page.header)
        for object in page.pageObjects:
            if object.type != 'table':
                print(object.data.text, StyleInfo(object.data.style), '', sep='\n')
