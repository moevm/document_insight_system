from bson import ObjectId
from flask_login import UserMixin

from main.checks_config.parser import sld_num


class Packable:
    def __init__(self, dictionary):
        pass

    def pack(self):
        return dict(vars(self))

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {', '.join([f'{key}: {value}' for key, value in vars(self).items()])}"


DEFAULT_PRESENTATION_CRITERIA = {'template_name': True,
                                 'slides_number': {'sld_num': sld_num['bsc'], 'detect_additional': True},
                                 'slides_enum': True, 'slides_headers': True, 'goals_slide': True, 'probe_slide': True,
                                 'actual_slide': True, 'conclusion_slide': True, 'slide_every_task': 50,
                                 'conclusion_actual': 50, 'conclusion_along': True}
DEFAULT_REPORT_CRITERIA = {'simple_check': True}


# You shouldn't create this or change username and presentations explicitly
class User(Packable, UserMixin):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        dictionary = dictionary or {}
        self.username = dictionary.get('username', '')
        self.name = dictionary.get('name', '')
        self.password_hash = dictionary.get('password_hash', '')
        self.presentations = dictionary.get('presentations', [])
        self.file_type = dictionary.get('file_type', 'pres')
        self.criteria = dictionary.get('enabled_checks',
                                       DEFAULT_REPORT_CRITERIA if self.file_type == 'report' else DEFAULT_PRESENTATION_CRITERIA)
        self.is_LTI = dictionary.get('is_LTI', False)
        self.lms_user_id = dictionary.get('lms_user_id', None)
        self.is_admin = dictionary.get('is_admin', False)
        self.params_for_passback = dictionary.get('params_for_passback', None)
        self.formats = dictionary.get('formats', [])

    def pack(self):
        package = super().pack()
        package['criteria'] = self.criteria
        return package

    def get_id(self):
        return self.username


class Consumers(Packable):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        dictionary = dictionary or {}
        self.consumer_key = dictionary.get('consumer_key', '')
        self.consumer_secret = dictionary.get('consumer_secret', '')
        self.timestamp_and_nonce = dictionary.get('timestamp_and_nonce', [])


class CriteriaPack(Packable):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        dictionary = dictionary or {}
        self.pack_name = dictionary.get('pack_name', '')
        self.enabled_checks = dictionary.get('enabled_checks', '')


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
        self.file_type = dictionary.get('file_type', 'pres')


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
        self.file_type = dictionary.get('file_type', 'pres')
        self.enabled_checks = dictionary.get('enabled_checks',
                                             DEFAULT_REPORT_CRITERIA if self.file_type == 'report' else DEFAULT_PRESENTATION_CRITERIA)
        self.is_failed = dictionary.get('is_failed', None)
        self.is_ended = dictionary.get('is_ended', None)

    def calc_score(self):
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