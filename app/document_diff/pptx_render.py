import os

from PIL import Image, ImageDraw
from pptx.enum.shapes import PP_PLACEHOLDER

from app.document_diff.pptx_alignment import normalize_text, text_similarity

COLORS = {
    'position': {'fill': (33, 150, 243, 60), 'border': (33, 150, 243, 255)},
    'modified': {'fill': (255, 152, 0, 60), 'border': (255, 152, 0, 255)},
    'added': {'fill': (76, 175, 80, 60), 'border': (76, 175, 80, 255)},
    'deleted': {'fill': (244, 67, 54, 60), 'border': (244, 67, 54, 255)},
}
POSITION_TOLERANCE = 0.005


def _is_footer(shape, height):
    placeholders = (PP_PLACEHOLDER.SLIDE_NUMBER, PP_PLACEHOLDER.FOOTER, PP_PLACEHOLDER.HEADER, PP_PLACEHOLDER.DATE)
    if shape.is_placeholder and shape.placeholder_format.type in placeholders:
        return True
    return shape.has_text_frame and shape.top.pt > height * 0.88 and len(shape.text.strip()) < 30


def shapes(slide, height):
    result = []
    for index, shape in enumerate(slide.shapes):
        if _is_footer(shape, height) or (not shape.has_text_frame and not shape.shape_type):
            continue
        result.append(
            {
                'index': index,
                'text': shape.text.strip() if shape.has_text_frame else '',
                'left': shape.left.pt,
                'top': shape.top.pt,
                'width': shape.width.pt,
                'height': shape.height.pt,
            }
        )
    return result


def match_shapes(shapes_a, shapes_b):
    matched, remaining_a, remaining_b = [], list(shapes_a), list(shapes_b)
    for shape_a in list(remaining_a):
        candidates = []
        for shape_b in remaining_b:
            distance = ((shape_a['left'] - shape_b['left']) ** 2 + (shape_a['top'] - shape_b['top']) ** 2) ** 0.5
            similarity = text_similarity(shape_a['text'], shape_b['text'])
            score = 0.7 * similarity + 0.3 * max(0, 1 - distance / 200)
            if similarity >= 0.4 or (similarity > 0.15 and distance < 40):
                candidates.append((score, shape_b))
        if candidates and max(candidates, key=lambda item: item[0])[0] > 0.45:
            _, shape_b = max(candidates, key=lambda item: item[0])
            matched.append((shape_a, shape_b))
            remaining_a.remove(shape_a)
            remaining_b.remove(shape_b)
    return matched, remaining_a, remaining_b


def draw_highlights(path, highlights, width, height):
    if not highlights or not os.path.exists(path):
        return
    with Image.open(path) as source:
        image = source.convert('RGBA')
    overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
    drawing = ImageDraw.Draw(overlay)
    for item in highlights:
        x0, y0 = item['left'] / width * image.width - 2, item['top'] / height * image.height - 2
        x1 = (item['left'] + item['width']) / width * image.width + 2
        y1 = (item['top'] + item['height']) / height * image.height + 2
        color = COLORS[item['type']]
        drawing.rectangle((x0, y0, x1, y1), fill=color['fill'], outline=color['border'], width=3)
    Image.alpha_composite(image, overlay).convert('RGB').save(path)
    image.close()
    overlay.close()


def _position_changed(shape_a, shape_b, dimensions_a, dimensions_b):
    width_a, height_a = dimensions_a
    width_b, height_b = dimensions_b
    return (
        abs(shape_a['left'] / width_a - shape_b['left'] / width_b) > POSITION_TOLERANCE
        or abs(shape_a['top'] / height_a - shape_b['top'] / height_b) > POSITION_TOLERANCE
    )


def slide_changes(slide_a, slide_b, dimensions_a, dimensions_b):
    matched, deleted, added = match_shapes(shapes(slide_a, dimensions_a[1]), shapes(slide_b, dimensions_b[1]))
    highlights_a = [{**shape, 'type': 'deleted'} for shape in deleted]
    highlights_b = [{**shape, 'type': 'added'} for shape in added]
    types = {'deleted'} if deleted else set()
    types.update({'added'} if added else set())
    for shape_a, shape_b in matched:
        if _position_changed(shape_a, shape_b, dimensions_a, dimensions_b):
            highlights_a.append({**shape_a, 'type': 'position'})
            highlights_b.append({**shape_b, 'type': 'position'})
            types.add('shift')
        if normalize_text(shape_a['text']) != normalize_text(shape_b['text']):
            highlights_a.append({**shape_a, 'type': 'modified'})
            highlights_b.append({**shape_b, 'type': 'modified'})
            types.add('modified')
    return highlights_a, highlights_b, types
