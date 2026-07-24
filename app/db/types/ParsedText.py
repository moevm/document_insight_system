from app.db.types.PackableWithId import PackableWithId


class ParsedText(PackableWithId):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        dictionary = dictionary or {}
        self.filename = dictionary.get('filename', '')
        self.parsed_chapters = dictionary.get('parsed_chapters', [])
