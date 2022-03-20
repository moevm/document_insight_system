import docx

from app.main.mse22.document.style_info import StyleInfo


class Document:
    def __init__(self, docx_document):
        core_props = docx_document.core_properties
        self.info = DocumentInfo(core_props.author, core_props.created, core_props.modified)
        self.pages = []
        current = []
        index = 0
        for par in docx_document.paragraphs:
            current.append(par)
            if 'w:br w:type="page"/' in par._element.xml:
                # create new_page from `current` and `index`
                # self.pages.append(new_page)
                current = []
                index += 1

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
    parsed_document = Document(docx_document)
    print(parsed_document)
    print()
    for paragraph in docx_document.paragraphs:
        style = StyleInfo(paragraph.style)
        print(style, "\n")
