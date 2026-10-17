from unittest.mock import MagicMock

import pytest
from main.checks.report_checks.watery_phrase_settings import WateryPhrase

from app.main.checks.report_checks.water_in_the_text_check import WaterInTheTextCheck


class TestWaterInTheTextCheck:
    @pytest.fixture
    def checker(self):
        mock_file_info = MagicMock()
        checker = WaterInTheTextCheck(mock_file_info)
        checker.watery_phrase = WateryPhrase.INTRODUCTORY_PHRASE
        checker.watery_words = WateryPhrase.SERVICE_WORDS + WateryPhrase.ABSTRACT_WORDS

        return checker

    def test_01_get_words(self, checker):
        check_text = "Это тест-пример! Он содержит? цифры 123 и дефис-слова."
        expected = ['это', 'тест-пример', 'он', 'содержит', 'цифры', 'и', 'дефис-слова']
        result = checker.get_words(check_text)

        assert result == expected

    def test_02_watery_phrase_density(self, checker):
        check_text = "Например, я пошел в магазин и купил хлеб."
        words = checker.get_words(check_text)
        density = checker.watery_phrase_density(check_text, words)
        expected_density = 0.375

        assert density == expected_density

    def test_03_long_sentences_density(self, checker):
        checker.long_sentence_word_limit = 5
        check_text = "Это короткое. Это предложение из шести слов для теста. Еще короткое."
        density = checker.long_sentences_density(check_text)
        expected_density = 0.25

        assert density == expected_density

    def test_04_meaningful_word_density(self, checker):
        words = ['стол', 'и', 'красивый', 'бежать', 'в', 'дом']
        density = checker.meaningful_word_density(words)
        expected_density = 4 / 6

        assert density == expected_density

    def test_05_valid_report(self):
        from types import SimpleNamespace

        file = SimpleNamespace(
            page_counter=lambda: 4,
            make_chapters=lambda _: [
                {
                    'text': 'Раздел',
                    'child': [{'text': 'Алгоритм обрабатывает изображения. Система анализирует данные.'}],
                }
            ],
        )
        info = {'file': file, 'file_type': {'type': 'report', 'report_type': 'VKR'}}
        assert WaterInTheTextCheck(info).check()['score'] == 1
