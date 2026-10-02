from pathlib import Path

def parse_report_fixture(report_path, pdf_path):
    if report_path.suffix.lower() == ".docx":
        from main.reports.docx_uploader import DocxUploader
        parsed_file = DocxUploader()
        parsed_file.upload(str(report_path), str(pdf_path) if pdf_path.exists() else "")
        parsed_file.parse()
        return parsed_file
    if report_path.suffix.lower() == ".md":
        from main.reports.md_uploader import MdUploader
        parsed_file = MdUploader(str(report_path))
        md_text = parsed_file.upload()
        parsed_file.parse(md_text)
        return parsed_file
    return None

def create_report_file_info(report_path, report_type="VKR", pdf_id=None):
    report_path = Path(report_path)
    pdf_path = report_path.with_suffix(".pdf")
    if not report_path.exists():
        raise AssertionError(f"Report fixture does not exist: {report_path}")
    parsed_file = parse_report_fixture(report_path, pdf_path)
    if parsed_file is None:
        raise AssertionError(f"Could not parse report fixture: {report_path}")
    return {
        "file": parsed_file,
        "filename": report_path.name,
        "pdf_id": pdf_id,
        "file_type": {
            "report_type": report_type,
            "type": report_type,
        },
    }
