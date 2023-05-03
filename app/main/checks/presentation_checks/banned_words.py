import re
from ..base_check import BasePresCriterion, answer, morph


class PresBannedWordsCheck(BasePresCriterion):
    description = "Проверка наличия запретных слов в презентации"
    id = 'pres_banned_words_check'

    def __init__(self, file_info, words=[], min_count=3, max_count=6):
        super().__init__(file_info)
        self.words = [morph.normal_forms(word)[0] for word in words]
        self.min_count = min_count
        self.max_count = max_count

    def check(self):
        detected_slides = {}
        result_str = f'<b>Запрещенные слова: {"; ".join(self.words)}</b><br>'
        count = 0
        for k, v in enumerate(self.file.get_text_from_slides()):
            lines_on_slides = re.split(r'\n', v)
            for index, line in enumerate(lines_on_slides):
                words_on_line = re.split(r'[^\w-]+', line)
                words_on_line = [morph.normal_forms(word)[0] for word in words_on_line]
                count_banned_words = set(words_on_line).intersection(self.words)
                if count_banned_words:
                    count += len(count_banned_words)
                    if k not in detected_slides.keys():
                        detected_slides[k] = []
                    detected_slides[k].append(f'[{index + 1}]: {line} <b>[{"; ".join(count_banned_words)}]</b>')
        if len(detected_slides):
            result_str += 'Обнаружены запретные слова! <br><br>'
            for k, v in detected_slides.items():
                result_str += f'Слайд №{k}:<br>{"<br>".join(detected_slides[k])}<br><br>'
        else:
            result_str = 'Пройдена!'
        result_score = 1
        if count > self.min_count:
            if count <= self.max_count:
                result_score = 0.5
            else:
                result_score = 0
        return answer(result_score, result_str)
