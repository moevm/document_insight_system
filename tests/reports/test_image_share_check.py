from unittest.mock import MagicMock

import pytest

from app.main.checks.report_checks.image_share_check import ReportImageShareCheck
from tests.util.report_file_utils import create_report_file_info


class TestReportImageShareCheck:
    report_dir = "image_share_check"
    
    def test_01_valid_share(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / self.report_dir / "valid.md")
        checker = ReportImageShareCheck(file_info, limit=0.5)
        file_info['file'].pdf_file.page_images = MagicMock(return_value=100)
        file_info['file'].pdf_file.page_height = MagicMock(return_value=1000)
        file_info['file'].pdf_file.page_images_count = MagicMock(return_value=8)
        result = checker.check()
        assert result["score"] == 1.0

    def test_02_too_many_images(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / self.report_dir / "invalid.md")
        checker = ReportImageShareCheck(file_info, limit=0.1)
        file_info['file'].pdf_file.page_images = MagicMock(return_value=500)
        file_info['file'].pdf_file.page_height = MagicMock(return_value=1000)
        result = checker.check()
        assert result["score"] == 0.0
        assert "документа без учета приложения" in result["verdict"][0]
    
    def test_03_too_few_count_images(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / self.report_dir / "invalid_too_few_cnt_img.docx")
        checker = ReportImageShareCheck(file_info, limit=1, min_cnt_img=3)
        result = checker.check()
        
        assert result["score"] == 0
        assert "1/3" in result["verdict"][0] # 1 - the number of images in the file, 3 - the minimum number of images

    def test_03_many_images_in_pril(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / self.report_dir / "invalid_many_images_in_pril.docx")
        checker = ReportImageShareCheck(file_info, limit=1, min_cnt_img=3)
        result = checker.check()
        
        assert result["score"] == 0
        assert "0/3" in result["verdict"][0]
    
    def test_04_valid_count_images(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / self.report_dir / "valid_count_images.docx")
        checker = ReportImageShareCheck(file_info, limit=1, min_cnt_img=3)
        result = checker.check()
        
        assert result["score"] == 1
    
    def test_05_valid_two_identical_on_once_page(self, reports_fixture_dir): # # Два идентичных рисунка на одной странице
        file_info = create_report_file_info(reports_fixture_dir / self.report_dir / "valid_two_identical_on_once_page.docx")
        checker = ReportImageShareCheck(file_info, limit=1, min_cnt_img=1)
        result = checker.check()
        
        assert result["score"] == 1
    
    def test_06_valid_images_is_watermark(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / self.report_dir / "valid_images_is_watermark.docx")
        checker = ReportImageShareCheck(file_info, limit=1, min_cnt_img=1)
        result = checker.check()
        
        assert result["score"] == 1
    
    def test_07_valid_images_with_alpha_channel(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / self.report_dir / "valid_images_with_alpha_channel.docx")
        checker = ReportImageShareCheck(file_info, limit=1, min_cnt_img=4)
        result = checker.check()

        assert result["score"] == 1

    def test_08_check_count_images_with_alphachanel(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / self.report_dir / "valid_images_with_alpha_channel.docx")
        checker = ReportImageShareCheck(file_info, limit=1, min_cnt_img=10)
        result = checker.check()

        assert "4/10" in result["verdict"][0]
    
    # TODO Добавить возможность считать диаграммы
    @pytest.mark.skip
    def test_09_find_diagrams(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / self.report_dir / "find_diagrams_in_report.docx")
        checker = ReportImageShareCheck(file_info, limit=1, min_cnt_img=10)
        result = checker.check()
        
        assert "1/10" in result["verdict"][0]
    
    # TODO Добавить возможность считать векторные рисунки
    @pytest.mark.skip
    def test_10_find_svg(self, reports_fixture_dir):
        file_info = create_report_file_info(reports_fixture_dir / self.report_dir / "find_svg.docx")
        checker = ReportImageShareCheck(file_info, limit=1, min_cnt_img=10)
        result = checker.check()
        
        assert "2/10" in result["verdict"][0]