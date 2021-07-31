import re
import itertools

def answer(mod, value, *args):
    return {
        'pass': bool(mod),
        'value': value,
        'verdict': (args)
    }

class BaseCheck:
    def __init__(self, presentation):
        self.presentation = presentation

    def check(self):
        raise NotImplementedError()


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


class TitleFormatCheck(BaseCheck):
    def __init__(self, presentation):
        super().__init__(presentation)
        self.empty_headers = []
        self.len_exceeded = []

    def exceeded_verdict(self):
        return 'Превышение длины: {}'.format(', '.join(map(str, self.len_exceeded))), \
               'Убедитесь в корректности заголовка и текста слайда'

    def empty_verdict(self):
        return 'Заголовки не найдены: {}.'.format(', '.join(map(str, self.empty_headers))), \
               'Убедитесь, что слайд озаглавлен соответстующим элементом'

    def get_failing_headers(self):
        for i, title in enumerate(self.presentation.get_titles(), 1):
            if title == "":
                self.empty_headers.append(i)
                continue

            title = str(title).replace('\x0b', '\n')
            if '\n' in title or '\r' in title:
                titles = [t for t in re.split('\r|\n', title) if t != '']
                if len(titles) > 2:
                    self.len_exceeded.append(i)

        return self.empty_headers, self.len_exceeded

    def check(self):
        self.get_failing_headers()
        error_slides = list(itertools.chain(self.empty_headers, self.len_exceeded))
        if not error_slides:
            return answer(not bool(error_slides), [self.empty_headers, self.len_exceeded], "Пройдена!")
        elif len(self.empty_headers) == 0 and len(self.len_exceeded) != 0:
            return answer(False, self.len_exceeded, *self.exceeded_verdict())
        elif len(self.empty_headers) != 0 and len(self.len_exceeded) == 0:
            return answer(False, self.empty_headers, *self.empty_verdict())
        else:
            return answer(False, [self.empty_headers, self.len_exceeded],
                   *list(itertools.chain(self.empty_verdict(), self.exceeded_verdict())))
