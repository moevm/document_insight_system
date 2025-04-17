import re
from db import db_methods

def parse_headers_and_pages_and_images(chapters, docx):
    text_on_page = docx.pdf_file.get_text_on_page()
    images = docx.images
    for page, text in text_on_page.items():
        text = re.sub(r"(-\n)", "", text)
        text = re.sub(r"\s\n", " ", text)
        if "СОДЕРЖАНИЕ" in text:
            continue
        for chapter in chapters:
            if chapter["header"] in text:
                chapter["start_page"] = page
        for image in images:
            if image.caption in text:
                db_methods.add_image_page(image._id, page)
    for chapter in chapters:
        for image in images:
            if image.caption in chapter["text"]:
                chapter["images"].append(image._id)
    return chapters


def parse_chapters(docx):
    chapters = []
    for chapter in docx.chapters:
        head = chapter["styled_text"]["text"]
        if "ПРИЛОЖЕНИЕ" in head:
            head = head.split(".")[0]
        if chapter["child"] != [] and "heading" in chapter["style"]:
            temp_text = ""
            for i in range(len(chapter["child"])):
                temp_text += chapter["child"][i]["styled_text"]["text"]
            chapters.append({"header": head, "start_page": 0, "text": temp_text, "images": []})
    return chapters