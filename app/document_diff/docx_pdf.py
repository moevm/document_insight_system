import difflib
import os

PALE_RED = (248 / 255, 215 / 255, 218 / 255)
PALE_GREEN = (214 / 255, 245 / 255, 214 / 255)
RED = (220 / 255, 53 / 255, 69 / 255)
GREEN = (0 / 255, 200 / 255, 0 / 255)
MAX_PHRASE_LENGTH = 40


def _word_diff(text_a, text_b):
    words_a, words_b = text_a.split(), text_b.split()
    changed_a, changed_b = [], []
    for tag, start_a, end_a, start_b, end_b in difflib.SequenceMatcher(None, words_a, words_b).get_opcodes():
        changed_a.extend((word, tag != 'equal') for word in words_a[start_a:end_a])
        changed_b.extend((word, tag != 'equal') for word in words_b[start_b:end_b])
    return changed_a, changed_b


def _changed_chunks(words):
    chunk = []
    for word, changed in words:
        if changed:
            chunk.append(word)
        elif chunk:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def _phrases(words, maximum_length=MAX_PHRASE_LENGTH):
    phrase, length = [], 0
    for word in words:
        if phrase and length + len(word) + 1 > maximum_length:
            yield ' '.join(phrase)
            phrase, length = [], 0
        phrase.append(word)
        length += len(word) + 1
    if phrase:
        yield ' '.join(phrase)


def _find(pdf, phrase, start_page):
    for page_number in list(range(start_page, len(pdf))) + list(range(start_page)):
        page = pdf[page_number]
        rectangles = page.search_for(phrase)
        if rectangles:
            return page, page_number, rectangles
    return None


def _annotate(page, rectangle, change):
    highlight = page.add_highlight_annot(rectangle)
    highlight.set_colors(stroke=PALE_RED if change == 'delete' else PALE_GREEN)
    highlight.set_opacity(0.6)
    highlight.update()
    if change == 'delete':
        strikeout = page.add_strikeout_annot(rectangle)
        strikeout.set_colors(stroke=RED)
        strikeout.update()
    else:
        underline = page.add_underline_annot(rectangle)
        underline.set_colors(stroke=GREEN)
        underline.update()


def highlight_words(pdf, words, change, start_page=0):
    location, page_number = None, start_page
    for phrase in _phrases(words):
        found = _find(pdf, phrase, page_number) or _find(pdf, ' '.join(phrase.split()[:3]), page_number)
        if found is None:
            continue
        page, page_number, rectangles = found
        for rectangle in rectangles:
            _annotate(page, rectangle, change)
        if location is None:
            location = {'page': page_number, 'y_ratio': rectangles[0].y0 / page.rect.height}
    return location, page_number


def _highlight_paragraphs(pdf, paragraphs, change, page_number):
    location = None
    for paragraph in paragraphs:
        found, page_number = highlight_words(pdf, paragraph.text.split(), change, page_number)
        location = location or found
    return location, page_number


def _highlight_replace(pdf_a, pdf_b, paragraphs_a, paragraphs_b, page_a, page_b):
    location_a = location_b = None
    for paragraph_a, paragraph_b in zip(paragraphs_a, paragraphs_b):
        words_a, words_b = _word_diff(paragraph_a.text, paragraph_b.text)
        for chunk in _changed_chunks(words_a):
            found, page_a = highlight_words(pdf_a, chunk, 'delete', page_a)
            location_a = location_a or found
        for chunk in _changed_chunks(words_b):
            found, page_b = highlight_words(pdf_b, chunk, 'insert', page_b)
            location_b = location_b or found
    return location_a, location_b, page_a, page_b


def collect_fragments(pdf_a, pdf_b, paragraphs_a, paragraphs_b, opcodes):
    fragments, page_a, page_b = [], 0, 0
    for number, (tag, start_a, end_a, start_b, end_b) in enumerate((item for item in opcodes if item[0] != 'equal'), 1):
        deleted, inserted = paragraphs_a[start_a:end_a], paragraphs_b[start_b:end_b]
        location_a = location_b = None
        if tag == 'delete':
            location_a, page_a = _highlight_paragraphs(pdf_a, deleted, 'delete', page_a)
        elif tag == 'insert':
            location_b, page_b = _highlight_paragraphs(pdf_b, inserted, 'insert', page_b)
        else:
            location_a, location_b, page_a, page_b = _highlight_replace(
                pdf_a, pdf_b, deleted, inserted, page_a, page_b
            )
            extra_a, page_a = _highlight_paragraphs(pdf_a, deleted[len(inserted):], 'delete', page_a)
            extra_b, page_b = _highlight_paragraphs(pdf_b, inserted[len(deleted):], 'insert', page_b)
            location_a, location_b = location_a or extra_a, location_b or extra_b
        fragments.append({'id': number, 'tag': tag, 'doc1': location_a, 'doc2': location_b})
    return fragments


def save_pdf(pdf, path):
    temporary_path = f'{path}.tmp'
    pdf.save(temporary_path)
    pdf.close()
    os.replace(temporary_path, path)
