import re

from app.db.methods.image import update_image

CONTENTS_PAGE_MARKERS = ('содержание',)
CAPTION_PREFIX_LENGTH = 20


def normalize_text(text):
    text = re.sub(r"(-\n)", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()


def _is_contents_page(text):
    return any(marker in text for marker in CONTENTS_PAGE_MARKERS)


def attach_pages_and_images_to_sections(sections, docx):
    text_on_page = docx.pdf_file.get_text_on_page()
    images = docx.images
    for page, text in text_on_page.items():
        text = normalize_text(text)
        if _is_contents_page(text):
            continue
        for section in sections:
            if not section['start_page'] and section['header'] in text:
                section['start_page'] = page
                for image in images:
                    if normalize_text(image.caption) in section['text'] and image._id not in section['images']:
                        section['images'].append(image._id)
        for image in images:
            if not image.page and normalize_text(image.caption)[:CAPTION_PREFIX_LENGTH] in text:
                image.page = page
                update_image(image)
    return sections


def chapters_to_sections(docx):
    sections = []
    for chapter in docx.chapters:
        if not chapter['child']:
            continue
        sections.append(
            {
                'header': chapter['text'].lower(),
                'start_page': 0,
                'text': normalize_text(' '.join(child['text'] for child in chapter['child'])),
                'images': [],
            }
        )
    return sections
