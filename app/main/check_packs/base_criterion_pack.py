from .utils import init_criterions


class BaseCriterionPack:

    def __init__(self, criterions, file_type, min_score=1.0, name=None):
        self.file_type = file_type
        self.name = name if name else self.__class__.__name__
        self.criterions = criterions
        self.min_score = min_score  # min score to pass

    def init(self, file_info):
        # create criterion objects, ignore errors - validation was performed earlier
        self.criterions, _ = init_criterions(self.criterions, file_type=self.file_type, file_info=file_info)

    def check(self):
        result = []
        for criterion in self.criterions:
            result.append(dict(
                id=criterion.id,
                name=criterion.name,
                **criterion.check()
            ))
        score = self.calc_score(result)
        return result, score, self.is_correct(score)

    def is_correct(self, score):
        return self.correct(score, self.min_score)

    @staticmethod
    def correct(score, min_score=1.0):
        return score >= min_score

    @staticmethod
    def calc_score(result):
        score = 0.
        for check in result:
            score += float(check['score'])
        return round(score, 3)
