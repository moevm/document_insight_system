import logging
from .utils import init_criterions

logger = logging.getLogger('root_logger')

PRIORITY_CHECK_FAILED_MSG = "<b>Данный критерий является обязательным для прохождения.<br>Результат всей проверки обнулен, но вы можете ознакомиться с результатами каждого критерия.</b><br>"
UNEXPECTED_CHECK_FAIL_MSG = "<b>Во время проверки произошла ошибка, попробуйте позже или обратитесь к администратору системы.<b>"

class BaseCriterionPack:

    def __init__(self, raw_criterions, file_type, point_levels, min_score=1, name=None, **kwargs):
        self.file_type = file_type
        self.name = name if name else self.__class__.__name__
        self.raw_criterions = raw_criterions
        self.criterions = []
        self.min_score = min_score  # min score to pass
        self.point_levels = point_levels

    def init(self, file_info):
        # create criterion objects, ignore errors - validation was performed earlier
        self.criterions, errors = init_criterions(self.raw_criterions, file_type=self.file_type, file_info=file_info)

    def check(self):
        result = []
        failed_priority_check = False
        for criterion in self.criterions:
            try:
                criterion_check_result = criterion.check()
            except Exception as e:
                logger.error(f'{criterion.id}: oшибка во время проверки: {e}')
                criterion_check_result = {'score': 0, 'verdict': [UNEXPECTED_CHECK_FAIL_MSG]}
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
            'min_score': self.min_score,
            'point_levels': self.point_levels,
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
