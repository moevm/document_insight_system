from .utils import init_criterions

PRIORITY_CHECK_FAILED_MSG = "<b>Данный критерий является обязательным для прохождения.<br>Результат всей проверки обнулен, но вы можете ознакомиться с результатами каждого критерия.</b><br>"


class BaseCriterionPack:

    def __init__(self, raw_criterions, file_type, min_score=1.0, name=None, **kwargs):
        self.file_type = file_type
        self.name = name if name else self.__class__.__name__
        self.raw_criterions = raw_criterions
        self.criterions = []
        self.min_score = min_score  # min score to pass

    def init(self, file_info):
        # create criterion objects, ignore errors - validation was performed earlier
        self.criterions, errors = init_criterions(self.raw_criterions, file_type=self.file_type, file_info=file_info)

    def check(self):
        result = []
        failed_priority_check = False
        for criterion in self.criterions:
            criterion_check_result = criterion.check()
            if criterion.priority and not criterion_check_result['score']:
                failed_priority_check = True
                criterion_check_result['verdict'] = [PRIORITY_CHECK_FAILED_MSG] + list(criterion_check_result['verdict'])
            result.append(dict(
                id=criterion.id,
                name=criterion.name,
                **criterion_check_result
            ))
        if failed_priority_check:  # if priority criterion is failed -> check is failed
            return result, 0, False
        score = self.calc_score(result)
        return result, score, self.is_correct(score)

    def is_correct(self, score):
        return self.correct(score, self.min_score)

    def to_json(self):
        # BASE_PRES_CRITERION, 'pres', min_score=1.0, name="BasePresentationCriterionPack"
        return {
            'name': self.name,
            'raw_criterions': self.raw_criterions,
            'file_type': self.file_type,
            'min_score': self.min_score
        }

    @staticmethod
    def correct(score, min_score=1.0):
        return score >= min_score

    @staticmethod
    def calc_score(result):
        if len(result) == 0: return 0.
        score = 0.
        for check in result:
            score += float(check['score'])
        return round(score / len(result), 3)
