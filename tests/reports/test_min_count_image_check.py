from unittest.mock import MagicMock

import pytest

from app.main.checks.report_checks.count_images_check import ReportCountImagesCheck
from app.main.reports.docx_uploader.docx_uploader import DocxUploader
from tests.util import create_report_file_info

class TestMinCountImageReportChecker:
    @pytest.mark.parametrize(
        "cnt_find_image, score",
        [
            (1, 0.0),
            (5, 0.0),
            (7, 0.0),
            (8, 1.0),
            (9, 1.0)
        ]
    )
    def test_01_correct_compression_with_founded_img(self, reports_fixture_dir, cnt_find_image, score):
        report_path = reports_fixture_dir / "min_cnt_image" / "invalid_images_in_pril.docx"
        file_info = create_report_file_info(report_path)
        docx_file: DocxUploader = file_info.get("file")
        
        docx_file.page_count = 10
        docx_file.pdf_file.page_images_count = MagicMock(return_value=cnt_find_image)
        
        checker = ReportCountImagesCheck(file_info)
        result = checker.check()
        
        assert result.get("score") == score
    
    @pytest.mark.parametrize(
        "count_page, answer_text",
        [
            (1, "В отчете недостаточно страниц. Нечего проверять."),
            (3, "В отчете недостаточно страниц. Нечего проверять."),
            (4, "В работе найдено"),
            (5, "В работе найдено")
        ]
    )
    def test_02_diff_cout_page(self, reports_fixture_dir, count_page, answer_text):
        report_path = reports_fixture_dir / "min_cnt_image" / "invalid_images_in_pril.docx"
        file_info = create_report_file_info(report_path)
        docx_file: DocxUploader = file_info.get("file")
        
        docx_file.page_count = count_page
        checker = ReportCountImagesCheck(file_info)
        result = checker.check()
        
        assert answer_text in result.get("verdict")[0]