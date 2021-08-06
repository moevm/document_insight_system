from app.main.checks.base_check import BaseCheck, answer
import re

class SldNumCheck(BaseCheck):
    def __init__(self, presentation, slides_number):
        super().__init__(presentation)
        self.slides_number = slides_number

    RANGE_VERDICTS = {
        'in_range': 'Количество слайдов в допустимых границах',
        'lt_min': 'Число слайдов меньше допустимого',
        'gt_max': 'Число слайдов превышает допустимое',
        'gt_max_suspected': 'Проверьте неозаглавленные запасные слайды'
        }

    def sldnum_verdict(self, find_additional, msg):
        return answer(False, find_additional, 'Всего: {}'.format(find_additional), \
                                              '{}. Допустимые границы: {}'.format(msg, self.slides_number))

    def get_sldnum_range(self, find_additional, suspected_additional = None):
        if self.slides_number[0] <= find_additional <= self.slides_number[1]:
            return answer(True, find_additional, self.RANGE_VERDICTS.get('in_range'))
        elif find_additional <= self.slides_number[0]:
            return self.sldnum_verdict(find_additional, self.RANGE_VERDICTS.get('lt_min'))
        else:
            if suspected_additional:
                return self.sldnum_verdict(find_additional, self.RANGE_VERDICTS.get('gt_max_suspected'))
            else:
                return self.sldnum_verdict(find_additional, self.RANGE_VERDICTS.get('gt_max'))

    def check(self):
        additional = re.compile('[А-Я][а-я]*[\s]слайд[ы]?')
        find_additional = [i for i, header in enumerate(self.presentation.get_titles()) if re.fullmatch(additional, header)]
        if len(find_additional) == 0:
            return self.get_sldnum_range(len(self.presentation.slides), suspected_additional = True)
        else:
            return self.get_sldnum_range(find_additional[0])
