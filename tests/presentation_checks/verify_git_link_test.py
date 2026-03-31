import pytest
from unittest.mock import Mock, patch
from app.main.checks.presentation_checks.verify_git_link import PresVerifyGitLinkCheck


class TestVerifyGitLink:
    def test_vgl1(self, mock_presentation):
        mock_presentation.get_text_from_slides.return_value = [
            "Текст без ссылок",
            "Обычный текст"
        ]

        check = PresVerifyGitLinkCheck(file=mock_presentation, deep_check=False)

        result = check.check()

        assert result.score == True
        assert "Нечего проверять" in result.message

    def test_vgl2(self):
        mock_presentation = Mock()
        mock_presentation.get_text_from_slides.return_value = [
            "Ссылка: https://github.com/username/nonexistent-repo"
        ]

        with patch('requests.get') as mock_get:
            mock_get.side_effect = ConnectionError("Connection error")

            check = PresVerifyGitLinkCheck(file=mock_presentation, deep_check=False)

            result = check.check()

            assert result.score == False
            assert "несуществующие или закрытые репозитории" in result.message

    def test_vgl3(self):
        mock_presentation = Mock()
        mock_presentation.get_text_from_slides.return_value = [
            "Ссылки: https://github.com/username/repo1, "
            "https://github.com/username/repo2, "
            "https://gitlab.com/username/repo3"
        ]

        def mock_request(url, *args, **kwargs):
            mock_response = Mock()
            if "repo2" in url:
                mock_response.status_code = 404
            else:
                mock_response.status_code = 200
            return mock_response

        with patch('requests.get', side_effect=mock_request):
            check = PresVerifyGitLinkCheck(file=mock_presentation, deep_check=False)

            result = check.check()

            assert result.score == False
            assert "repo2" in result.message