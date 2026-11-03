from pymodm import EmbeddedMongoModel, MongoModel, fields


class ParsedChapter(EmbeddedMongoModel):
    header = fields.CharField()
    start_page = fields.IntegerField(default=0)
    text = fields.CharField(default='')
    images = fields.ListField(field=fields.ObjectIdField(), default=list)

    class Meta:
        final = True


class ParsedText(MongoModel):
    filename = fields.CharField()
    parsed_chapters = fields.EmbeddedDocumentListField(ParsedChapter, default=list)

    class Meta:
        collection_name = 'parsed_texts'
        final = True
