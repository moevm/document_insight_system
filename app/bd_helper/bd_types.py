from flask_login import UserMixin


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
            self.conclusion_actual = 0
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

    def correct(self):
        return (
            (self.slides_number == -1 or self.slides_number['pass']) and
            (self.slides_enum == -1 or self.slides_enum['pass']) and
            (self.slides_headers == -1 or self.slides_headers['pass']) and
            (self.goals_slide == -1 or self.goals_slide['pass']) and
            (self.probe_slide == -1 or self.probe_slide['pass']) and
            (self.actual_slide == -1 or self.actual_slide['pass']) and
            (self.conclusion_slide == -1 or self.conclusion_slide['pass']) and
            (self.conclusion_actual == -1 or self.conclusion_actual['pass'])
        )

    def __str__(self) -> str:
        return ("Checks: { " + (("_id: " + str(self._id) + ", ") if hasattr(self, "_id") else "") +
                "slides_number: " + str(self.slides_number) + ", " +
                "slides_enum: " + str(self.slides_enum) + ", " +
                "slides_headers: " + str(self.slides_headers) + ", " +
                "goals_slide: " + str(self.goals_slide) + ", " +
                "probe_slide: " + str(self.probe_slide) + ", " +
                "actual_slide: " + str(self.actual_slide) + ", " +
                "conclusion_slide: " + str(self.conclusion_slide) + ", " +
                "conclusion_actual: " + str(self.conclusion_actual) + " }")
