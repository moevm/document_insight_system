from app.db.types.PackableWithId import PackableWithId
from app.main.check_packs import DEFAULT_TYPE_INFO


class Presentation(PackableWithId):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        dictionary = dictionary or {}
        self.name = dictionary.get('name', '')
        self.checks = dictionary.get('checks', [])
        self.file_type = dictionary.get('file_type', DEFAULT_TYPE_INFO)
