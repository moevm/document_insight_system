import re

from ..base_check import BaseReportCriterion, answer


class AppendixReferenceCheck(BaseReportCriterion):
    label = "Проверка наличия ссылок на все приложения"
    id = "appendix_reference_check"

    tag_pattern = re.compile(r'<[^>]+>')
    header_pattern = re.compile(r'^\s*приложение\s+([А-ЯЁ])\b', re.IGNORECASE)
    ref_pattern = re.compile(r'(?i:приложени(?:ях|ями|ям|е|и|я|ю|й))\s+([А-ЯЁ]\b(?:(?:\s*,\s*|\s+и\s+)[А-ЯЁ]\b)*)')
    ref_separator_pattern = re.compile(r'\s*,\s*|\s+и\s+')

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

    def _collect_references(self):
        references = set()
        for chapter in self.chapters:
            if self._appendix_letter(chapter):
                break
            for child in chapter["child"]:
                for match in self.ref_pattern.finditer(child["text"]):
                    for letter in self.ref_separator_pattern.split(match.group(1)):
                        references.add(letter.upper())
        return references

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
