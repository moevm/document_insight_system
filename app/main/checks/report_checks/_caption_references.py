import re
from collections import Counter

from docx.oxml.ns import qn

from ..base_check import BaseReportCriterion, answer


class CaptionReferences(BaseReportCriterion):
    caption_word = ''
    reference_pattern = ''

    def check(self):
        chapters = self.file.make_chapters(self.file_type['report_type'])
        if not chapters:
            return answer(False, 'Не найдено ни одного заголовка.')
        numbers, text_parts, body_children = [], [], []
        for chapter in chapters:
            if re.search(
                r'список\s+(?:использованных\s+)?(?:источников|литературы)|^приложение', chapter['text'], re.I
            ):
                break
            for child in chapter['child']:
                body_children.append(child)
                match = re.match(self.caption_word + r'\s+(\d+(?:\.\d+)*)\b', child['text'], re.I)
                if child['style'] == self.caption_style.lower() and match:
                    numbers.append(match.group(1))
                else:
                    text_parts.append(child['text'])
        references = set()
        for text in text_parts:
            for match in re.finditer(self.reference_pattern + r'\s*((?:\d+(?:\.\d+)*\s*[,;]?\s*)+)', text, re.I):
                references.update(re.findall(r'\d+(?:\.\d+)*', match.group(1)))
        captions = set(numbers)
        errors = []
        duplicate = [number for number, count in Counter(numbers).items() if count > 1]
        if duplicate:
            errors.append('Повторяются номера подписей: ' + ', '.join(duplicate))
        if references - captions:
            errors.append('Упомянуты несуществующие объекты: ' + ', '.join(sorted(references - captions)))
        if captions - references:
            errors.append('Нет ссылок на объекты: ' + ', '.join(sorted(captions - references)))
        if not captions:
            if self.is_markdown:
                has_images = any(child.get('styled_text', {}).get('image_count', 0) for child in body_children)
                has_tables = any(child['style'] == 'md_table' for child in body_children)
            else:
                document = getattr(self.file, 'file', None)
                has_images = has_tables = in_body = False
                if document is not None:
                    for element in document.element.body:
                        text = ''.join(node.text or '' for node in element.iter(qn('w:t')))
                        if text.strip().lower() == chapters[0]['text'].strip().lower():
                            in_body = True
                        if re.search(r'^приложение|^список\s', text, re.I):
                            break
                        if in_body:
                            has_tables = has_tables or element.tag.endswith('}tbl')
                            has_images = has_images or any(
                                node.tag in (qn('w:drawing'), qn('w:pict')) for node in element.iter()
                            )
            if self.caption_word == 'Рисунок' and has_images:
                errors.append('В основном тексте есть рисунки, но не найдены их подписи.')
            if self.caption_word == 'Таблица' and has_tables:
                errors.append('В основном тексте есть таблицы, но не найдены их подписи.')
        return answer(not errors, '<br>'.join(errors) or 'Пройдена!')
