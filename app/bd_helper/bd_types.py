from flask_login import UserMixin


class Packable:
    def __init__(self, dictionary):
        pass

    def pack(self):
        return vars(self)


# You shouldn't create this or change username and presentations explicitly
class User(Packable, UserMixin):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        if dictionary is None:
            self.username = ''
            self.name = ''
            self.password_hash = ''
            self.presentations = []
            self.is_admin = False
        else:
            self.username = dictionary['username']
            self.name = dictionary['name']
            self.password_hash = dictionary['password_hash']
            self.presentations = dictionary['presentations']
            self.is_admin = dictionary['is_admin']

    def __str__(self) -> str:
        return ("User: { username: " + self.username + ", " +
                "name: " + self.name + ", " +
                "password_hash: " + str(self.password_hash) + ", " +
                "presentations: " + str(self.presentations) + ", " +
                "is_admin: " + str(self.is_admin) + " }")

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


PERCENTAGE_OF_SIMILARITY = 60


# You shouldn't create or change this explicitly
class Checks(Packable):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        if dictionary is None:
            self.slides_number = ''
            self.slides_enum = ''
            self.slides_headers = ''
            self.goals_slide = ''
            self.probe_slide = ''
            self.actual_slide = ''
            self.conclusion_slide = ''
            self.conclusion_actual = 0
        else:
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
        return (self.slides_number == '' and self.slides_enum == '' and self.slides_headers == '' and
                self.goals_slide != '' and self.probe_slide != '' and self.actual_slide != '' and
                self.conclusion_slide != '' and self.conclusion_actual >= PERCENTAGE_OF_SIMILARITY)

    def __str__(self) -> str:
        return ("Checks: { " + (("_id: " + str(self._id) + ", ") if hasattr(self, "_id") else "") +
                "slides_number: " + self.slides_number + ", " +
                "slides_enum: " + self.slides_enum + ", " +
                "slides_headers: " + self.slides_headers + ", " +
                "goals_slide: " + self.goals_slide + ", " +
                "probe_slide: " + self.probe_slide + ", " +
                "actual_slide: " + self.actual_slide + ", " +
                "conclusion_slide: " + self.conclusion_slide +
                "conclusion_actual: " + self.conclusion_actual + " }")
