class CoreProperties:
    def __init__(self, doc):
        self.author = doc.core_properties.author
        self.category = doc.core_properties.category
        self.comments = doc.core_properties.comments
        self.content_status = doc.core_properties.content_status
        self.created = doc.core_properties.created
        self.identifier = doc.core_properties.identifier
        self.keywords = doc.core_properties.keywords
        self.language = doc.core_properties.language
        self.last_modified_by = doc.core_properties.last_modified_by
        self.last_printed = doc.core_properties.last_printed
        self.modified = doc.core_properties.modified
        self.revision = doc.core_properties.revision
        self.subject = doc.core_properties.subject
        self.title = doc.core_properties.title
        self.version = doc.core_properties.version

    def print_file_info(self):
        print('AUTHOR: ', self.author)
        print('CATEGORY: ', self.category)
        print('COMMENTS: ', self.comments)
        print('CONTENT STATUS: ', self.content_status)
        print('CREATED: ', self.created)
        print('IDENTIFIED: ', self.identifier)
        print('KEYWORDS: ', self.keywords)
        print('LAST MODIFIED BY: ', self.last_modified_by)
        print('LAST PRINTED: ', self.last_printed)
        print('MODIFIED: ', self.modified)
        print('REVISION: ', self.revision)
        print('SUBJECT: ', self.subject)
        print('TITLE: ', self.title)
        print('VERSION: ', self.version)
        print()
