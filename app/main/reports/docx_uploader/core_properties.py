import pandas


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

    def to_string(self):
        df = pandas.DataFrame({'Values': [self.author, self.category, self.comments, self.content_status, self.created,
                                          self.identifier, self.keywords, self.language, self.last_modified_by,
                                          self.last_printed, self.modified, self.revision, self.subject, self.title,
                                          self.version]})
        df.index = ['AUTHOR', 'CATEGORY', 'COMMENTS', 'CONTENT STATUS', 'CREATED', 'IDENTIFIED', 'KEYWORDS', 'LANGUAGE',
                    'LAST MODIFIED BY', 'LAST PRINTED', 'MODIFIED', 'REVISION', 'SUBJECT', 'TITLE', 'VERSION']
        return df.to_string()
