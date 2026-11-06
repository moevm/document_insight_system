import difflib
import re

from PIL import Image

from app.document_diff.config import (
    PPTX_ALIGNMENT_FLOAT_TOLERANCE,
    PPTX_DHASH_SIZE,
    PPTX_MIN_SLIDE_SIMILARITY,
    PPTX_SLIDE_TEXT_WEIGHT,
    PPTX_SLIDE_VISUAL_WEIGHT,
)


def dhash(image, hash_size=PPTX_DHASH_SIZE):
    resampling = getattr(Image, 'Resampling', Image).LANCZOS
    pixels = list(image.convert('L').resize((hash_size + 1, hash_size), resampling).getdata())
    value = 0
    for row in range(hash_size):
        for column in range(hash_size):
            offset = row * (hash_size + 1) + column
            value = (value << 1) | (pixels[offset] > pixels[offset + 1])
    return value


def normalize_text(text):
    text = re.sub(r'[\u200b\u200c\u200d\ufeff\x0b\x0c]', '', text or '').replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', text).strip()


def _alignment_text(text):
    page_number = r'\b(стр\.|страница|page|слайд)?\s*\d+(\s*[\/из]\s*\d+)?\b'
    return re.sub(page_number, '', normalize_text(text), flags=re.IGNORECASE).strip()


def text_similarity(text_a, text_b):
    text_a, text_b = _alignment_text(text_a), _alignment_text(text_b)
    if not text_a and not text_b:
        return 1.0
    if not text_a or not text_b:
        return 0.0
    return difflib.SequenceMatcher(None, text_a.split(), text_b.split()).ratio()


def _slide_similarity(slides_a, slides_b):
    result = []
    for slide_a in slides_a:
        row = []
        for slide_b in slides_b:
            visual = 1 - (slide_a['dhash'] ^ slide_b['dhash']).bit_count() / (PPTX_DHASH_SIZE**2)
            row.append(
                PPTX_SLIDE_TEXT_WEIGHT * text_similarity(slide_a['text'], slide_b['text'])
                + PPTX_SLIDE_VISUAL_WEIGHT * max(0, visual)
            )
        result.append(row)
    return result


def align_slides(slides_a, slides_b, minimum_similarity=PPTX_MIN_SLIDE_SIMILARITY):
    rows, columns = len(slides_a), len(slides_b)
    similarity = _slide_similarity(slides_a, slides_b)
    scores = [[0.0] * (columns + 1) for _ in range(rows + 1)]
    for row in range(1, rows + 1):
        for column in range(1, columns + 1):
            matched = scores[row - 1][column - 1] + similarity[row - 1][column - 1]
            scores[row][column] = max(
                scores[row - 1][column],
                scores[row][column - 1],
                matched if similarity[row - 1][column - 1] >= minimum_similarity else -1,
            )
    aligned, row, column = [], rows, columns
    while row and column:
        value = similarity[row - 1][column - 1]
        is_match = abs(scores[row][column] - scores[row - 1][column - 1] - value) < PPTX_ALIGNMENT_FLOAT_TOLERANCE
        if value >= minimum_similarity and is_match:
            aligned.append((row - 1, column - 1))
            row, column = row - 1, column - 1
        elif abs(scores[row][column] - scores[row - 1][column]) < PPTX_ALIGNMENT_FLOAT_TOLERANCE:
            row -= 1
        else:
            column -= 1
    aligned.reverse()
    return _with_unmatched_slides(aligned, rows, columns)


def _with_unmatched_slides(aligned, rows, columns):
    mapping, index_a, index_b = [], 0, 0
    for matched_a, matched_b in aligned + [(rows, columns)]:
        while index_a < matched_a:
            mapping.append({'status': 'deleted', 'slide_a': index_a, 'slide_b': None})
            index_a += 1
        while index_b < matched_b:
            mapping.append({'status': 'added', 'slide_a': None, 'slide_b': index_b})
            index_b += 1
        if matched_a < rows:
            mapping.append({'status': 'matched', 'slide_a': matched_a, 'slide_b': matched_b})
            index_a, index_b = index_a + 1, index_b + 1
    return mapping
