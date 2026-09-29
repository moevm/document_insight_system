import re

from ..base_check import BaseReportCriterion, answer


class AppendixReferenceCheck(BaseReportCriterion):
    label = "Проверка наличия ссылок на все приложения"
    id = "appendix_reference_check"

    header_pattern = re.compile(r'(?i)приложение ([А-ЯЁа-яё])')
    ref_pattern = re.compile(r'(?i)приложени[еияюй]\s+([А-ЯЁа-яё])')

    def __init__(self, file_info):
        super().__init__(file_info)
        self.chapters = []

    def late_init(self):
        self.chapters = self.file.make_chapters(self.file_type['report_type'])

    def _collect_appendices(self):
        appendices = set()
        for chapter in self.chapters:
            match = self.header_pattern.search(chapter["text"])
            if match:
                appendices.add(match.group(1))
        return appendices

    def _collect_references(self):
        references = set()
        for chapter in self.chapters:
            if self.header_pattern.search(chapter["text"]):
                break
            for child in chapter["child"]:
                for match in self.ref_pattern.finditer(child["text"]):
                    references.add(match.group(1).upper())
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
