import pytest
from unittest.mock import patch
from app.main.checks.presentation_checks.banned_words import PresBannedWordsCheck


class TestBannedWords:
    def test_bw1(self, mock_file):
        mock_file.get_text_from_slides.return_value = ["Хороший текст", "Отличный доклад"]

        with patch('pymorphy2.MorphAnalyzer') as mock_morph:
            mock_morph.return_value.normal_forms.return_value = ["хороший", "текст", "отличный", "доклад"]
            check = PresBannedWordsCheck(
                words=["плохой", "ужасный"],
                min_count=1,
                max_count=3,
                file=mock_file
            )

            result = check.check()

            assert result.score == 1
            assert result.message == 'Пройдена!'
            assert not hasattr(check, 'detected_slides') or check.detected_slides == []

    def test_bw2(self, mock_file):
        mock_file.get_text_from_slides.return_value = ["Любой текст"]
        check = PresBannedWordsCheck(
            words=[],
            min_count=1,
            max_count=3,
            file=mock_file
        )

        result = check.check()

        assert result.score == 1
        assert result.message == 'Пройдена!'