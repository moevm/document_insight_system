import re

from docx.document import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from ..base_check import BaseReportCriterion, answer, morph


class AppendixReferenceCheck(BaseReportCriterion):
    label = "Проверка наличия ссылок на все приложения"
    id = "appendix_reference_check"

    tag_pattern = re.compile(r'<[^>]+>')
    header_pattern = re.compile(r'^\s*приложение\s+([А-ЯЁ])\b', re.IGNORECASE)
    ref_letter = r'[А-ЯЁ]\b'
    ref_separator = r'(?:\s*,\s*|\s+и\s+)'
    ref_pattern = re.compile(rf'\b((?i:приложени\w*))\s+({ref_letter}(?:{ref_separator}{ref_letter})*)')
    ref_separator_pattern = re.compile(ref_separator)
    prev_word_pattern = re.compile(r'(\w+)\s+$')
    governing_pos = {'NOUN', 'ADJF', 'PRTF', 'NPRO'}

    def __init__(self, file_info):
        super().__init__(file_info)
        self.chapters = []

    def late_init(self):
        self.chapters = self.file.make_chapters(self.file_type['report_type'])

    def _appendix_letter(self, chapter):
        match = self.header_pattern.search(self.tag_pattern.sub('', chapter["text"]))
        return match.group(1).upper() if match else None

    def _collect_appendices(self):
        appendices = set()
        for chapter in self.chapters:
            letter = self._appendix_letter(chapter)
            if letter:
                appendices.add(letter)
        return appendices

    def _is_application_mention(self, word, text_before):
        parses = [p for p in morph.parse(word.lower()) if p.normal_form == 'приложение']
        if not parses:
            return True
        if not any('gent' in p.tag for p in parses):
            return False
        prev = self.prev_word_pattern.search(text_before)
        if not prev:
            return False
        return morph.parse(prev.group(1).lower())[0].tag.POS in self.governing_pos

    def _find_references(self, text):
        references = set()
        text = self.tag_pattern.sub('', text)
        for match in self.ref_pattern.finditer(text):
            if self._is_application_mention(match.group(1), text[: match.start()]):
                continue
            references.update(self.ref_separator_pattern.split(match.group(2)))
        return references

    def _collect_md_references(self):
        references = set()
        for chapter in self.chapters:
            if self._appendix_letter(chapter):
                break
            for child in chapter["child"]:
                references |= self._find_references(child["text"])
        return references

    def _docx_blocks(self, document):
        for element in document.element.body.iterchildren():
            if element.tag == qn('w:p'):
                yield Paragraph(element, document)
            elif element.tag == qn('w:tbl'):
                yield Table(element, document)

    def _collect_docx_references(self, document):
        references = set()
        in_chapter = False
        for block in self._docx_blocks(document):
            if isinstance(block, Table):
                if in_chapter:
                    for row in block.rows:
                        for cell in row.cells:
                            references |= self._find_references(cell.text)
            elif block.style is not None and 'heading' in block.style.name.lower():
                if self.header_pattern.search(block.text):
                    break
                in_chapter = True
            elif in_chapter:
                references |= self._find_references(block.text)
        return references

    def _collect_references(self):
        document = getattr(self.file, 'file', None)
        if isinstance(document, Document):
            return self._collect_docx_references(document)
        return self._collect_md_references()

    def check(self):
        self.late_init()

        appendices = self._collect_appendices()
        if not appendices:
            return answer(True, "Приложения не найдены.")

        references = self._collect_references()
        unreferenced = appendices - references

        if not unreferenced:
            return answer(True, "Пройдена!")

        return answer(
            False,
            f'Не упомянуты в тексте следующие приложения: {", ".join(sorted(unreferenced))}',
        )
