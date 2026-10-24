import re

from app.nlp.tokenization import content_lemmas

from ..base_check import BaseReportCriterion, answer


class SWKeywordsCheck(BaseReportCriterion):
    label = 'Проверка наличия раздела "Ключевые слова" и упоминания их в тексте'
    _description = 'Ключевые слова идут после названия работы и упоминаются в тексте.'
    id = 'sw_keywords_check'

    def __init__(self, file_info, min_key_words=3):
        super().__init__(file_info)
        self.min_key_words = min_key_words

    def check(self):
        if not self.is_markdown:
            return answer(False, 'Критерий предназначен для отчётов Markdown.')
        paragraphs = self.file.styled_paragraphs
        if len(paragraphs) < 2:
            return answer(False, 'Раздел "Ключевые слова" не найден')
        key_text = paragraphs[1]['text']
        if not re.match(r'^Ключевые слова\s*:', key_text, re.I):
            return answer(False, 'Раздел "Ключевые слова" не найден')
        keywords = [word.strip() for word in key_text.split(':', 1)[1].split(',') if word.strip()]
        if len(set(word.lower() for word in keywords)) < self.min_key_words:
            return answer(False, f'Не пройдена! Количество ключевых слов должно быть не менее {self.min_key_words}')
        text = ' '.join(par['text'] for par in paragraphs[2:])
        lemmas = ' '.join(content_lemmas(text))
        missing = [
            phrase
            for phrase in keywords
            if not content_lemmas(phrase) or ' '.join(content_lemmas(phrase)) not in lemmas
        ]
        if missing:
            return answer(False, 'Не пройдена! В тексте не найдены следующие ключевые слова: ' + ', '.join(missing))
        return answer(True, 'Пройдена!')

    def text_to_lemma(self, text):
        return ' '.join(content_lemmas(re.sub(r'<[^>]*>', '', text)))
