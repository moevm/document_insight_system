import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

project_root = Path(__file__).parent.parent.parent
tests_path = str(project_root / "tests")
if tests_path in sys.path:
    sys.path.remove(tests_path)
sys.path.insert(0, str(project_root / "app"))


@pytest.fixture
def reports_fixture_dir():
    return Path(__file__).parent.parent / "fixtures" / "reports"


@pytest.fixture(autouse=True)
def auto_patch_uploader(monkeypatch):

    from types import ModuleType

    import main.reports.md_uploader.md_uploader as legacy_md_module
    from main.reports.md_uploader.md_uploader import MdUploader

    import app.main.reports.md_uploader.md_uploader as md_module

    core = ModuleType('md2pdf.core')
    core.md2pdf = lambda *args, **kwargs: None
    monkeypatch.setitem(sys.modules, 'md2pdf', ModuleType('md2pdf'))
    monkeypatch.setitem(sys.modules, 'md2pdf.core', core)
    pdf = MagicMock()
    pdf.page_count_all = 1
    pdf.text_on_page = {1: 'Sample text on page'}
    pdf.get_text_on_page.return_value = pdf.text_on_page
    pdf.get_image_num.return_value = 0
    pdf.page_images.return_value = 0
    pdf.page_height.return_value = 1000
    monkeypatch.setattr(md_module, 'PdfDocumentManager', lambda *a, **k: pdf)
    monkeypatch.setattr(legacy_md_module, 'PdfDocumentManager', lambda *a, **k: pdf)

    original_parse = MdUploader.parse

    def patched_parse(self, md_text):
        res = original_parse(self, md_text)
        self.headers_main = "Test Title"

        def make_headers(work_type):
            if work_type == 'VKR':
                headers = [
                    {"name": "Титульный лист", "marker": False, "key": "титульный лист", "page": 1},
                    {
                        "name": "Задание на выпускную квалификационную работу",
                        "marker": False,
                        "key": "задание",
                        "page": 2,
                    },
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

    monkeypatch.setattr(MdUploader, "parse", patched_parse)
    monkeypatch.setattr(md_module.MdUploader, "parse", patched_parse)
    yield
