from flask_login import UserMixin
from app.main.checks_config.parser import sld_num

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
        self.criteria = dictionary.get('criteria', {'slides_number': {'sld_num': sld_num['bsc'], 'detect_additional': True},
                                              'slides_enum': True, 'slides_headers': True, 'goals_slide': True, 'probe_slide': True,
                                              'actual_slide': True, 'conclusion_slide': True, 'slide_every_task': 50,
                                              'conclusion_actual': 50, 'conclusion_along': True})
        self.is_LTI = dictionary.get('is_LTI', False)
        self.is_admin = dictionary.get('is_admin', False)
        self.params_for_passback = dictionary.get('params_for_passback', None)

    def pack(self):
        package = super(User, self).pack()
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


# You shouldn't create or change this explicitly
class Presentation(Packable):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        dictionary = dictionary or {}
        if '_id' in dictionary:
            self._id = dictionary.get('_id')
        self.name = dictionary.get('name', '')
        self.checks = dictionary.get('checks', [])


class Logs(Packable):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        dictionary = dictionary or {}
        if '_id' in dictionary:
            self._id = dictionary.get('_id', '')
        self.timestamp = dictionary.get('timestamp', None)
        self.serviceName = dictionary.get('serviceName', None)
        self.levelname = dictionary.get('levelname', None)
        self.levelno = dictionary.get('levelno', None)
        self.message = dictionary.get('message', None)
        self.pathname = dictionary.get('pathname', None)
        self.filename = dictionary.get('filename', None)
        self.funcName = dictionary.get('funcName', None)
        self.lineno = dictionary.get('lineno', None)

# You shouldn't create or change this explicitly
class Checks(Packable):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        dictionary = dictionary or {}
        if '_id' in dictionary:
            self._id = dictionary.get('_id', '')

        self.enabled_checks = dictionary.get('enabled_checks', {'slides_number': {'sld_num': sld_num['bsc'], 'detect_additional': True},
                                              'slides_enum': True, 'slides_headers': True, 'goals_slide': True, 'probe_slide': True,
                                              'actual_slide': True, 'conclusion_slide': True, 'slide_every_task': 50,
                                              'conclusion_actual': 50, 'conclusion_along': True})
        self.score = dictionary.get('score', -1)
        self.filename = dictionary.get('filename', '')
        self.conv_pdf_fs_id = dictionary.get('conv_pdf_fs_id', '')
        self.user = dictionary.get('user', '')
        self.is_passbacked = dictionary.get('is_passbacked', None)
        self.lms_passback_time = dictionary.get('lms_passback_time', None)

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
