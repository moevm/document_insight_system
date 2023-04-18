import re

from utils import format_header

from ..base_check import BasePresCriterion, answer


class SldNumCheck(BasePresCriterion):
    description = "Количество основных слайдов"
    id = 'slides_number'

    def __init__(self, file_info, slides_number, detect_additional=True):
        super().__init__(file_info)
        self.slides_number = slides_number
        self.detect_additional = detect_additional

    RANGE_VERDICTS = {
        'in_range': 'Количество слайдов в допустимых границах',
        'lt_min': 'Число слайдов меньше допустимого',
        'gt_max': 'Число слайдов превышает допустимое',
        'gt_max_suspected': 'Проверьте, что запасные слайды расположенны после слайда с заголовком “Запасные слайды”'
    }

    def sldnum_verdict(self, find_additional, msg):
        return answer(False, format_header('Всего: {}'.format(find_additional)),
                      '{}. Допустимые границы: {}'.format(msg, self.slides_number))

    def get_sldnum_range(self, find_additional, suspected_additional=None):
        if self.slides_number[0] <= find_additional <= self.slides_number[1]:
            return answer(True, self.RANGE_VERDICTS.get('in_range'))
        elif find_additional <= self.slides_number[0]:
            return self.sldnum_verdict(find_additional, self.RANGE_VERDICTS.get('lt_min'))
        else:
            if suspected_additional and self.detect_additional:
                return self.sldnum_verdict(find_additional, self.RANGE_VERDICTS.get('gt_max_suspected'))
            else:
                return self.sldnum_verdict(find_additional, self.RANGE_VERDICTS.get('gt_max'))

    def check(self):
        if self.detect_additional:
            additional = re.compile('[А-Я][а-я]*[\s]слайд[ы]?')
            find_additional = [i for i, header in enumerate(self.file.get_titles()) if re.fullmatch(additional, header)]
            if len(find_additional) == 0:
                return self.get_sldnum_range(len(self.file.slides), suspected_additional=True)
            else:
                return self.get_sldnum_range(find_additional[0])
        else:
            return self.get_sldnum_range(self.file.get_len_slides())
