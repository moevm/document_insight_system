import sys
from pathlib import Path
from types import ModuleType

import docx
import markdown
import pymupdf
import pytest
from lxml import html

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'app'))


@pytest.fixture
def make_pdf(tmp_path):
    def create(texts):
        path = tmp_path / f'document-{len(list(tmp_path.glob("*.pdf")))}.pdf'
        document = pymupdf.open()
        for text in texts:
            page = document.new_page()
            page.insert_text((72, 72), text)
        document.save(path)
        document.close()
        return path

    return create


@pytest.fixture
def md_document(tmp_path, monkeypatch, make_pdf):
    from app.main.reports.md_uploader.md_uploader import MdUploader

    core = ModuleType('md2pdf.core')

    def convert(output, md_content=None, **kwargs):
        text = html.fragment_fromstring(
            markdown.markdown(md_content, extensions=['tables']), create_parent='div'
        ).text_content()
        source = make_pdf([text])
        Path(output).write_bytes(source.read_bytes())
        # md2pdf returns None; the uploader must use the output path.

    core.md2pdf = convert
    monkeypatch.setitem(sys.modules, 'md2pdf', ModuleType('md2pdf'))
    monkeypatch.setitem(sys.modules, 'md2pdf.core', core)

    def create(text):
        path = tmp_path / 'assignment.version.md'
        path.write_text(text)
        uploader = MdUploader(str(path))
        uploader.parse(text)
        return {
            'file': uploader,
            'filename': path.name,
            'pdf_id': 'test',
            'file_type': {'type': 'report', 'report_type': 'VKR'},
        }

    return create


@pytest.fixture
def docx_document(tmp_path, make_pdf):
    from app.main.reports.docx_uploader.docx_uploader import DocxUploader

    def create(document=None, pdf_texts=None, report_type='VKR'):
        path = tmp_path / 'report.docx'
        (document or docx.Document()).save(path)
        pdf = make_pdf(pdf_texts or ['title', 'task', 'contents', 'body'])
        uploader = DocxUploader()
        uploader.upload(str(path), str(pdf))
        uploader.parse()
        return {
            'file': uploader,
            'filename': path.name,
            'pdf_id': 'test',
            'file_type': {'type': 'report', 'report_type': report_type},
        }

    return create
