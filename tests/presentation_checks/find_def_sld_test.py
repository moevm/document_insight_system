import pytest
from app.main.checks.presentation_checks.find_def_sld import FindDefSld


class TestFindDefSld:
    def test_fds1(self, mock_file):
        mock_file.get_titles.return_value = ["Титульный слайд", "Введение", "Заключение"]
        mock_file.get_text_from_slides.return_value = ["Текст слайда 1", "Текст слайда 2", "Текст слайда 3"]
        mock_file.found_index = {}
        def mock_format_page_link(indexes):
            return [str(idx + 1) for idx in indexes]
        mock_file.format_page_link = mock_format_page_link
        check = FindDefSld(
            type_of_slide="Введение",
            file=mock_file
        )

        result = check.check()

        assert result.score == True
        assert "Найден под номером: 2" in result.message
        assert check.found_idxs == [1]
        assert mock_file.found_index["введение"] == [1]

    def test_fds2(self, mock_file):
        mock_file.get_titles.return_value = ["ВВЕДЕНИЕ", "ЗАКЛЮЧЕНИЕ"]
        def mock_format_page_link(indexes):
            return [str(idx + 1) for idx in indexes]
        mock_file.format_page_link = mock_format_page_link
        check = FindDefSld(
            type_of_slide="введение",
            file=mock_file
        )

        result = check.check()

        assert result.score == True
        assert "Найден под номером: 1" in result.message
        assert check.found_idxs == [0]

    def test_fds3(self, mock_file):
        mock_file.get_titles.return_value = ["Первый слайд", "Второй слайд", "Заключение"]
        mock_file.found_index = {}
        def mock_format_page_link(indexes):
            return [str(idx + 1) for idx in indexes]
        mock_file.format_page_link = mock_format_page_link

        check = FindDefSld(
            type_of_slide="слайд",
            file=mock_file
        )

        result = check.check()

        assert result.score == True
        assert "1, 2" in result.message
        assert check.found_idxs == [0, 1]
        assert mock_file.found_index["слайд"] == [0, 1]