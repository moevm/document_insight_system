from app.nlp.tokenization import content_lemmas

from ..base_check import BasePresCriterion, answer


class FindThemeInPres(BasePresCriterion):
    label = 'Проверка упоминания темы в заголовках презентации'
    _description = 'Слова темы титульного слайда встречаются в остальных заголовках.'
    id = 'theme_in_pres_check'

    def __init__(self, file_info, skip_slides_nums=(1,), skip_slides_titles=('Заключение',), limit=60, theme=None):
        super().__init__(file_info)
        self.skip_slides_nums = skip_slides_nums
        self.skip_slides_titles = skip_slides_titles
        self.limit = limit
        self.theme = theme
        if not 0 < limit <= 100:
            raise ValueError('limit должен быть в пределах (0; 100].')

    def check(self):
        titles = self.file.get_titles()
        if not titles:
            return answer(False, 'В презентации нет слайдов.')
        theme = set(content_lemmas(self.theme if self.theme is not None else titles[0]))
        if not theme:
            return answer(False, 'Не удалось определить тему презентации по титульному заголовку.')
        text = ' '.join(
            title
            for index, title in enumerate(titles, 1)
            if index not in self.skip_slides_nums
            and not any(skip.lower() in title.lower() for skip in self.skip_slides_titles)
        )
        percent = round(len(theme & set(content_lemmas(text))) * 100 / len(theme))
        score = min(percent / self.limit, 1)
        return answer(score, f'Процент упоминания темы в заголовках: {percent}%; требуется {self.limit}%.')
