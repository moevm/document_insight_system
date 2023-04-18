import docx

from .chapter import ChapterCreator, StyleInfo


class Document:
    def __init__(self, docx_document, filename, chapter_names):
        core_props = docx_document.core_properties
        self.info = DocumentInfo(core_props.author, core_props.created, core_props.modified)
        self.chapters, self.errors = ChapterCreator().create_chapter_objects(filename, chapter_names)

    def __str__(self):
        if not self.errors:
            s = "The document contains all the basic sections."
        else:
            s = "There are no sections in the document: "
            for i in self.errors:
                s += i + ", "
        return s + "\ndocument.Document object:\nPages:\n{0}\nInfo: {1}".format(self.chapters, self.info)


class DocumentInfo:
    def __init__(self, author, datetime_created, datetime_modified):
        self.author = author
        self.datetime_created = datetime_created
        self.datetime_modified = datetime_modified

    def __str__(self):
        return "document.DocumentInfo object:\nAuthor: {0}\nCreated: {1}\nModified: {2}" \
            .format(self.author, self.datetime_created, self.datetime_modified)


def main(args):
    if args.type == 'LR' or args.type == 'FWQ':
        docx_document = docx.Document(args.filename)
        parsed_document = Document(docx_document, args.filename, args.type)
        print(parsed_document)
        print()
        for page in parsed_document.chapters:
            print(page.header)
            for object in page.pageObjects:
                if object.type != 'table':
                    print(object.data.text, StyleInfo(object.data.style), '', sep='\n')
    else:
        print('Wrong file type!')
