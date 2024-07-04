from app.db.db_types import UserMixin
from app.db.types.Packable import Packable
from app.main.check_packs import BASE_PACKS, DEFAULT_REPORT_TYPE_INFO

# You shouldn't create this or change username and presentations explicitly

class User(Packable, UserMixin):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        dictionary = dictionary or {}
        self.username = dictionary.get('username', '')
        self.name = dictionary.get('name', '')
        self.password_hash = dictionary.get('password_hash', '')
        self.presentations = dictionary.get('presentations', [])
        self.file_type = dictionary.get('file_type', DEFAULT_REPORT_TYPE_INFO)
        try:
            self.criteria = dictionary.get('criteria', BASE_PACKS.get(self.file_type['type']).name)
        except:
            self.criteria = dictionary.get('criteria', BASE_PACKS.get(self.file_type).name)
        self.is_LTI = dictionary.get('is_LTI', False)
        self.lms_user_id = dictionary.get('lms_user_id', None)
        self.is_admin = dictionary.get('is_admin', False)
        self.params_for_passback = dictionary.get('params_for_passback', None)
        self.formats = dictionary.get('formats', [])
        self.two_files = dictionary.get('two_files', False)

    def get_id(self):
        return self.username