import re

from app.nlp.text_similarity import NLPProcessor


def content_and_intro(file, report_type):
    chapters = file.make_chapters(report_type)
    intro = next((chapter for chapter in chapters if 'введение' in chapter['text'].lower()), None)
    content = {}
    for chapter in chapters:
        title = chapter['text']
        if re.search(r'^приложение|список\s+(?:использованных\s+)?(?:источников|литературы)', title, re.I):
            break
        if 'введение' not in title.lower():
            text = '\n'.join(child['text'] for child in chapter['child'])
            if text.strip():
                content[title] = text
    return intro, content


def introduction_tasks(intro):
    tasks, collecting = [], False
    if not intro:
        return tasks
    for child in intro['child']:
        text = child['text'].strip()
        if re.search(r'\bобъект\w*|\bпредмет\w*|практическая значимость', text, re.I):
            if collecting:
                break
        if re.search(r'\bзадач[аиуы]?\b', text, re.I):
            collecting = True
            remainder = text.split(':', 1)[1].strip() if ':' in text else ''
            if remainder:
                tasks.append(remainder)
        elif collecting and text:
            tasks.append(text)
    return tasks


def content_similarity(text, chapters):
    return NLPProcessor().calculate_cosine_similarity(text, chapters)
