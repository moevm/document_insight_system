import pandas as pd

class CoreProperties:
    def __init__(
        self,
        author=None,
        category=None,
        comments=None,
        content_status=None,
        created=None,
        identifier=None,
        keywords=None,
        language=None,
        last_modified_by=None,
        last_printed=None,
        modified=None,
        revision=None,
        subject=None,
        title=None,
        version=None,
        date=None, 
        university=None, # Название вуза
        faculty=None,    # Факультет
        department=None, # Кафедра
        speciality=None, # Специальность
        degree=None      # Уровень образования
    ):
        self.author = author
        self.category = category
        self.comments = comments
        self.content_status = content_status
        self.created = created
        self.identifier = identifier
        self.keywords = keywords
        self.language = language
        self.last_modified_by = last_modified_by
        self.last_printed = last_printed
        self.modified = modified
        self.revision = revision
        self.subject = subject
        self.title = title
        self.version = version
        self.date = date
        self.university = university
        self.faculty = faculty
        self.department = department
        self.speciality = speciality
        self.degree = degree

    @staticmethod
    def from_doc(doc):
        return CoreProperties(
            author=doc.core_properties.author,
            category=doc.core_properties.category,
            comments=doc.core_properties.comments,
            content_status=doc.core_properties.content_status,
            created=doc.core_properties.created,
            identifier=doc.core_properties.identifier,
            keywords=doc.core_properties.keywords,
            language=doc.core_properties.language,
            last_modified_by=doc.core_properties.last_modified_by,
            last_printed=doc.core_properties.last_printed,
            modified=doc.core_properties.modified,
            revision=doc.core_properties.revision,
            subject=doc.core_properties.subject,
            title=doc.core_properties.title,
            version=doc.core_properties.version
        )

    def to_string(self):
        df = pd.DataFrame({'Values': [
            self.author, self.category, self.comments, self.content_status, self.created,
            self.identifier, self.keywords, self.language, self.last_modified_by,
            self.last_printed, self.modified, self.revision, self.subject, self.title,
            self.version, self.date, self.university, self.faculty, self.department, 
            self.speciality, self.degree
        ]})
        df.index = [
            'AUTHOR', 'CATEGORY', 'COMMENTS', 'CONTENT STATUS', 'CREATED', 'IDENTIFIER', 'KEYWORDS', 'LANGUAGE',
            'LAST MODIFIED BY', 'LAST PRINTED', 'MODIFIED', 'REVISION', 'SUBJECT', 'TITLE', 'VERSION', 'DATE', 
            'UNIVERSITY', 'FACULTY', 'DEEPARTMENT', 'SPECIALITY', 'DEGREE'
        ]
        return df.to_string()
