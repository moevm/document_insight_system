from ..base_check import BasePresCriterion, answer


class SlideTextVolumeCheck(BasePresCriterion):
    label = 'Заголовки слайдов не дублируются'
    description = 'Проверка на дублируемость заголовков слайдов'
    id = 'slide_text_volume_check'

    def __init__(self, file_info, min_count_words_on_slide=40,
                 min_count_paragraphs=2, min_count_words_in_paragraph=20,
                 max_count_words_on_slide=100, max_count_paragraphs=5,
                 max_count_words_in_paragraph=50,
                 slides_with_required_list=["Цели и задачи", "Заключение"]):
        super().__init__(file_info)
        self.min_count_words_on_slide = min_count_words_on_slide
        self.min_count_paragraphs = min_count_paragraphs
        self.min_count_words_in_paragraph = min_count_words_in_paragraph
        self.max_count_words_on_slide = max_count_words_on_slide
        self.max_count_paragraphs = max_count_paragraphs
        self.max_count_words_in_paragraph = max_count_words_in_paragraph
        self.slides_with_required_list = slides_with_required_list

    def check(self):
        result_str = ''
        if not result_str:
            return answer(True, 'Пройдена!')
        else:
            return answer(False, result_str)