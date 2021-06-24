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
        if dictionary is None:
            self.username = ''
            self.name = ''
            self.password_hash = ''
            self.presentations = []
            self.criteria = Checks()
            self.is_admin = False
        else:
            self.username = dictionary['username']
            self.name = dictionary['name']
            self.password_hash = dictionary['password_hash']
            self.presentations = dictionary['presentations']
            self.criteria = Checks(dictionary['criteria'])
            self.is_admin = dictionary['is_admin']

    def __str__(self) -> str:
        return ("User: { username: " + self.username + ", " +
                "name: " + self.name + ", " +
                "password_hash: " + str(self.password_hash) + ", " +
                "presentations: " + str(self.presentations) + ", " +
                "personal criteria: " + str(self.criteria) + ", " +
                "is_admin: " + str(self.is_admin) + " }")

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
        if dictionary is None:
            self.name = ''
            self.checks = []
        else:
            self._id = dictionary['_id']
            self.name = dictionary['name']
            self.checks = dictionary['checks']

    def __str__(self) -> str:
        return ("Presentation: { " + (("_id: " + str(self._id) + ", ") if hasattr(self, "_id") else "") +
                "name: " + self.name + ", " +
                "checks: " + str(self.checks) + " }")


# You shouldn't create or change this explicitly
class Checks(Packable):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        if dictionary is None:
            self.slides_number = 12
            self.slides_enum = 0
            self.slides_headers = 0
            self.goals_slide = 0
            self.probe_slide = 0
            self.actual_slide = 0
            self.conclusion_slide = 0
            self.conclusion_actual = 50
            self.conclusion_along = 0
            self.slide_every_task = 50
            self.score = -1
            self.filename = ''
            self.user = ''
        else:
            if '_id' in dictionary:
                self._id = dictionary['_id']
            self.slides_number = dictionary['slides_number']
            self.slides_enum = dictionary['slides_enum']
            self.slides_headers = dictionary['slides_headers']
            self.goals_slide = dictionary['goals_slide']
            self.probe_slide = dictionary['probe_slide']
            self.actual_slide = dictionary['actual_slide']
            self.conclusion_slide = dictionary['conclusion_slide']
            self.conclusion_actual = dictionary['conclusion_actual']
            self.conclusion_along = dictionary['conclusion_along']
            self.slide_every_task = dictionary['slide_every_task']
            self.score = -1
            self.filename = ''
            self.user = ''

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
                logger.error('Try checking the disabled_parameters list, there might be a missing value')
                pass

        return (numerical_score, enabled_value)

    def correct(self):
        return all([check == -1 or check['pass'] for check in self.get_checks().values()])

    def __str__(self) -> str:
        return ("Checks: { " + (("_id: " + str(self._id) + ", ") if hasattr(self, "_id") else "") +
                "slides_number: " + str(self.slides_number) + ", " +
                "slides_enum: " + str(self.slides_enum) + ", " +
                "slides_headers: " + str(self.slides_headers) + ", " +
                "goals_slide: " + str(self.goals_slide) + ", " +
                "probe_slide: " + str(self.probe_slide) + ", " +
                "actual_slide: " + str(self.actual_slide) + ", " +
                "conclusion_slide: " + str(self.conclusion_slide) + ", " +
                "conclusion_actual: " + str(self.conclusion_actual) + ", " +
                "conclusion_along: " + str(self.conclusion_along) + ", " +
                "slide_every_task: " + str(self.slide_every_task) + ", " +
                "score: " + str(self.score) + ", " +
                "filename: " + str(self.filename) + ", " +
                "username: " + str( self.user) +
                " }")
