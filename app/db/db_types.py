from bson import ObjectId
from flask_login import UserMixin

from main.check_packs import BASE_PACKS, BaseCriterionPack, DEFAULT_TYPE_INFO, DEFAULT_REPORT_TYPE_INFO

class Packable:
    def __init__(self, dictionary):
        pass

    def pack(self):
        return dict(vars(self))

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {', '.join([f'{key}: {value}' for key, value in vars(self).items()])}"


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


class Consumers(Packable):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        dictionary = dictionary or {}
        self.consumer_key = dictionary.get('consumer_key', '')
        self.consumer_secret = dictionary.get('consumer_secret', '')
        self.timestamp_and_nonce = dictionary.get('timestamp_and_nonce', [])


class PackableWithId(Packable):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        dictionary = dictionary or {}
        if '_id' in dictionary:
            self._id = ObjectId(dictionary.get('_id'))

    def pack(self, to_str=False):
        package = super().pack()
        if '_id' in package: package['_id'] = self._id if not to_str else str(self._id)
        return package


# You shouldn't create or change this explicitly
class Presentation(PackableWithId):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        dictionary = dictionary or {}
        self.name = dictionary.get('name', '')
        self.checks = dictionary.get('checks', [])
        self.file_type = dictionary.get('file_type', DEFAULT_TYPE_INFO)


class Logs(Packable):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        dictionary = dictionary or {}
        self.timestamp = dictionary.get('timestamp', None)
        self.serviceName = dictionary.get('serviceName', None)
        self.levelname = dictionary.get('levelname', None)
        self.levelno = dictionary.get('levelno', None)
        self.message = dictionary.get('message', None)
        self.pathname = dictionary.get('pathname', None)
        self.filename = dictionary.get('filename', None)
        self.funcName = dictionary.get('funcName', None)
        self.lineno = dictionary.get('lineno', None)


class Check(PackableWithId):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        dictionary = dictionary or {}
        self.filename = dictionary.get('filename', '')
        self.conv_pdf_fs_id = dictionary.get('conv_pdf_fs_id', '')
        self.user = dictionary.get('user', '')
        self.lms_user_id = dictionary.get('lms_user_id', None)
        self.is_passbacked = dictionary.get('is_passbacked', None)
        self.lms_passback_time = dictionary.get('lms_passback_time', None)
        self.score = dictionary.get('score', -1)
        self.file_type = dictionary.get('file_type', DEFAULT_TYPE_INFO)
        self.enabled_checks = dictionary.get('enabled_checks', BASE_PACKS.get(self.file_type['type']).name)
        self.criteria = dictionary.get('criteria', BASE_PACKS.get(self.file_type['type']).name)
        self.params_for_passback = dictionary.get('params_for_passback', None)
        self.is_failed = dictionary.get('is_failed', None)
        self.is_ended = dictionary.get('is_ended', True)
        self.is_passed = dictionary.get('is_passed', int(self.score) == 1)

    def calc_score(self):
        # check after implementation criterion pack
        if isinstance(self.enabled_checks, (list,)):
            return BaseCriterionPack.calc_score(self.enabled_checks)
        # old check
        enabled_checks = dict((k, v) for k, v in self.enabled_checks.items() if v)
        enabled_value = len([check for check in enabled_checks.values() if check])
        numerical_score = 0
        for check in enabled_checks.values():
            try:
                if check.get('pass'):
                    numerical_score += 1
            except TypeError:
                pass

        return float("{:.3f}".format(numerical_score / enabled_value))

    def correct(self):
        # check after implementation criterion pack
        if isinstance(self.enabled_checks, (list,)):
            return self.is_passed
        # old check
        return all([check == False or check['pass'] for check in self.enabled_checks.values()])

    def pack(self, to_str=False):
        package = super().pack(to_str)
        package['conv_pdf_fs_id'] = self.conv_pdf_fs_id if not to_str else str(self.conv_pdf_fs_id)
        package['enabled_checks'] = self.enabled_checks
        return package

    def get_flags(self):
        def none_to_true(x):
            return x is None or bool(x)

        def none_to_false(x):
            return x is not None and bool(x)

        is_ended = none_to_true(self.is_ended)  # None for old checks => True, True->True, False->False
        is_failed = none_to_false(self.is_failed)  # None for old checks => False, True->True, False->False
        return {'is_ended': is_ended, 'is_failed': is_failed}
