import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock

mock_md2pdf_module = MagicMock()
mock_md2pdf_module.core.md2pdf.return_value = "mock.pdf"
sys.modules["md2pdf"] = mock_md2pdf_module
sys.modules["md2pdf.core"] = mock_md2pdf_module.core

mock_pymupdf = MagicMock()
mock_doc = MagicMock()
mock_doc.page_count = 1
mock_page = MagicMock()
mock_page.get_text.return_value = "Sample text on page"
mock_page.rect = MagicMock(height=1000, y0=50, y1=950)
mock_doc.load_page.return_value = mock_page
mock_doc.__getitem__.return_value = mock_page
mock_doc.get_page_images.return_value = []
mock_pymupdf.open.return_value = mock_doc
sys.modules["pymupdf"] = mock_pymupdf
sys.modules["fitz"] = mock_pymupdf

project_root = Path(__file__).parent.parent.parent
tests_path = str(project_root / "tests")
if tests_path in sys.path:
    sys.path.remove(tests_path)
sys.path.insert(0, str(project_root / "app"))

@pytest.fixture
def reports_fixture_dir():
    return Path(__file__).parent.parent / "fixtures" / "reports"

@pytest.fixture(autouse=True)
def auto_patch_uploader():

    from main.reports.md_uploader.md_uploader import MdUploader

    original_parse = MdUploader.parse

    def patched_parse(self, md_text):
        res = original_parse(self, md_text)
        self.headers_main = "Test Title"

        def make_headers(work_type):
            if work_type == 'VKR':
                headers = [
                    {"name": "Титульный лист", "marker": False, "key": "титульный лист", "page": 1},
                    {"name": "Задание на выпускную квалификационную работу", "marker": False, "key": "задание", "page": 2},
                    {"name": "Календарный план", "marker": False, "key": "календарный план", "page": 3},
                    {"name": "Реферат", "marker": False, "key": "реферат", "page": 4},
                    {"name": "Abstract", "marker": False, "key": "abstract", "page": 5},
                    {"name": "Содержание", "marker": False, "key": "содержание", "page": 6},
                ]
                chapters = self.make_chapters(work_type)
                for h in headers:
                    for c in chapters:
                        if h["key"] in c["text"].lower():
                            h["marker"] = True
                            h["page"] = c["number"] // 10 + 1
                return headers
            return []

        def find_images_vkr(work_type):
            images_counter = 0
            all_numbers = set()
            import re
            for paragraph in self.styled_paragraphs:
                if paragraph['runs'][0]['style'] == "вкр_подпись для рисунков":
                    text = paragraph['text'].lower()
                    found = re.findall(r'рисунок\s*(\d+)', text)
                    for num in found:
                        images_counter += 1
                        all_numbers.add(int(num))
            return images_counter, all_numbers

        self.make_headers = make_headers
        self.find_images_vkr = find_images_vkr

        orig_find_lit = self.find_literature_page
        self.find_literature_page = lambda work_type=None: orig_find_lit(work_type)

        return res

    MdUploader.parse = patched_parse
    yield
    MdUploader.parse = original_parse
