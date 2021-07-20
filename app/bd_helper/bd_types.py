from flask_login import UserMixin
from logging import getLogger
logger = getLogger('root')

class Packable:
    def __init__(self, dictionary):
        pass

    def pack(self):
        return dict(vars(self))


# You shouldn't create this or change username and presentations explicitly
class User(Packable, UserMixin):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        dictionary = dictionary or {}
        self.username = dictionary.get('username', '')
        self.name = dictionary.get('name', '')
        self.password_hash = dictionary.get('password_hash', '')
        self.presentations = dictionary.get('presentations', [])
        self.criteria = Checks(dictionary.get('criteria'))
        self.is_admin = dictionary.get('is_admin', False)

    def __str__(self) -> str:
        return f"User: {', '.join([f'{key}: {value}' for key, value in vars(self).items()])}"

    def pack(self):
        package = super(User, self).pack()
        package['criteria'] = self.criteria.pack()
        return package

    def get_id(self):
        return self.username


# You shouldn't create or change this explicitly
class Presentation(Packable):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        dictionary = dictionary or {}
        if '_id' in dictionary:
            self._id = dictionary.get('_id')
        self.name = dictionary.get('name', '')
        self.checks = dictionary.get('checks', [])

    def __str__(self) -> str:
        return f"Presentation: {', '.join([f'{key}: {value}' for key, value in vars(self).items()])}"


# You shouldn't create or change this explicitly
class Checks(Packable):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        dictionary = dictionary or {}
        if '_id' in dictionary:
            self._id = dictionary.get('_id', '')
        self.slides_number = dictionary.get('slides_number', 12)
        self.slides_enum = dictionary.get('slides_enum', 0)
        self.slides_headers = dictionary.get('slides_headers', 0)
        self.goals_slide = dictionary.get('goals_slide', 0)
        self.probe_slide = dictionary.get('probe_slide', 0)
        self.actual_slide = dictionary.get('actual_slide', 0)
        self.conclusion_slide = dictionary.get('conclusion_slide', 0)
        self.conclusion_actual = dictionary.get('conclusion_actual', 50)
        self.conclusion_along = dictionary.get('conclusion_along', 0)
        self.slide_every_task = dictionary.get('slide_every_task', 50)
        self.score = dictionary.get('score', -1)
        self.filename = dictionary.get('filename', '')
        self.user = dictionary.get('user', '')

    def get_checks(self):
        return dict(
            slides_number = self.slides_number,
            slides_enum = self.slides_enum,
            slides_headers = self.slides_headers,
            goals_slide = self.goals_slide,
            probe_slide = self.probe_slide,
            actual_slide = self.actual_slide,
            conclusion_slide = self.conclusion_slide,
            conclusion_actual = self.conclusion_actual,
            conclusion_along = self.conclusion_along,
            slide_every_task = self.slide_every_task,
        )

    def calc_score(self):
        enabled_checks = self.get_checks()
        enabled_value = len([check for check in enabled_checks.values() if check != -1])
        numerical_score = 0
        for check in enabled_checks.values():
            try:
                if check != -1 and check['pass']:
                    numerical_score += 1
            except TypeError:
                pass

        return float("{:.3f}".format(numerical_score / enabled_value))

    def correct(self):
        return all([check == -1 or check['pass'] for check in self.get_checks().values()])

    def __str__(self) -> str:
        return f"Checks: {', '.join([f'{key}: {value}' for key, value in vars(self).items()])}"
