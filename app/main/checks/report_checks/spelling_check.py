from language_tool_python import LanguageTool, exceptions
from ..base_check import BaseReportCriterion, answer
from time import perf_counter
from typing import Iterator
from logging import getLogger


logger = getLogger(__name__)


class LanguageToolWrapper:
    client = None
    # TODO: remote_server url from config

    def __init__(self, fixed_suggestion: int = 2):
        if not self.__class__.client:
            self.__class__.client = LanguageTool('ru-RU', mother_tongue='ru', remote_server="languagetool:8010")
        self.rules_sort = (
            'MORFOLOGIK_RULE_RU_RU',
            'Verb_comma_Verb', 'GDE_COMMA', 'A_NO_DA', 'CHTO_COMMA',
            'RU_SIMPLE_REPLACE', 'PREP_O_and_Noun', 'PREP_C_and_Noun', 'S_SO'
        )
        self.errors = {ruleid: dict(suggestions=[], no_suggestions=[]) for ruleid in self.rules_sort}
        self.perf = {"check_pages": {"full": 0, "pages": []}, "check": []}
        self.fixed_suggestion = fixed_suggestion
        self.error_counter = 0

    def check_pages(self, pages: Iterator[tuple[int, str]]) -> list:
        all_start = perf_counter()
        for page_num, text_on_page in pages:
            start_page = perf_counter()
            possible_errors = self.check(text_on_page)
            self.error_counter += len(possible_errors)
            for possible_error in possible_errors:
                if possible_error.rule_id not in self.errors:
                    continue    # if we don't track this ruleid
                # Сохраняем только self.fixed_suggestion предложений по замене.
                suggestions = list(filter(lambda x: x.strip(), possible_error.replacements[:self.fixed_suggestion]))
                # Сохраняем контекст ошибки.
                context = possible_error.context
                error_text = f"Ошибка на стр. {page_num}. " \
                    f"   Контекст: {context}"
                if suggestions:
                    error_text += f"   Возможные исправления: {suggestions}"
                self.errors[possible_error.rule_id][("no_" if not suggestions else "") + "suggestions"].append(
                    error_text
                )
            end_page = perf_counter()
            self.perf['check_pages']['pages'].append(end_page-start_page)
        self.perf['check_pages']['full'] = perf_counter()-all_start

    def check(self, text: str) -> list:
        start = perf_counter()
        result = self.client.check(text)
        self.perf['check'].append(perf_counter()-start)
        return result

    def get_format_result(self):
        result_strs = [f"Найдены следующие ошибки написания (общее их число - {self.error_counter})<br>"]
        for ruleid in self.rules_sort:
            rule_errors = self.errors[ruleid]
            suggestions = rule_errors['suggestions']
            no_suggestions = rule_errors['no_suggestions']
            if suggestions or no_suggestions:
                result_strs.append(f"<b>Тип ошибки {ruleid}</b><ul>")
                if suggestions:
                    result_strs.append(f"""
<li>Ошибки с предложениями авто-исправления:</li>
    <ul>
        <li>{'</li><li>'.join(suggestions)}</li>
    </ul>""")
                if no_suggestions:
                    result_strs.append(f"""
<li>Ошибки без авто-исправлений - обратите на них внимание:</li>
    <ul>
        <li>{'</li><li>'.join(no_suggestions)}</li>
    </ul>""")
                result_strs.append('</ul>')
        return ''.join(result_strs)

    def stats(self):
        return f"""
All time: {self.perf['check_pages']['full']}
Pages: {len(self.perf['check_pages']['pages'])}
Pages time: {sum(self.perf['check_pages']['pages'])}
Avg page time: {sum(self.perf['check_pages']['pages'])/len(self.perf['check_pages']['pages'])}
Min page time: {min(self.perf['check_pages']['pages'])}
Max page time: {max(self.perf['check_pages']['pages'])}
rule_ids: {self.rules_sort}
"""


class SpellingCheck(BaseReportCriterion):
    label = "Проверка наличия орфографических ошибок в тексте."
    _description = ''
    id = 'spelling_check'
    warning = True

    def __init__(self, file_info, min_errors_count=5, max_errors_count=400):
        super().__init__(file_info)
        self.min_errors_count = min_errors_count
        self.max_errors_count = max_errors_count

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        try:
            spell_checker = LanguageToolWrapper()
            if (literature_page := self.file.find_literature_page()):
                literature_page -= 1    # page before literature
            main_text_page = 3

            spell_checker.check_pages(
                enumerate(
                    self.file.pdf_file.get_text_on_page(start_page=main_text_page, end_page=literature_page).values(),
                    start=main_text_page,
                )
            )
        except exceptions.LanguageToolError as exc:
            logger.error(f"LanguageToolError: {exc}")
            return answer(0, "Сервер проверки орфографии сейчас недоступен - проверка пропущена.")

        logger.debug(spell_checker.stats())

        feedback = """<h5>Обращаем внимание, что:</h5>
<ul>
    <li>критерий носит рекомендательный характер и не влияет на оценку отчёта</li>
    <li>проверка может содержать ошибочные результаты, т.к. не учитывает специфику вашего текста / темы / пр.</li>
    <li>ниже приведен список вероятных ошибок в тексте - ознакомьтесь и исправьте ошибки, если они действительно есть</li>
</ul>
<br>"""
        grade = 0
        if spell_checker.error_counter <= self.min_errors_count:
            return answer(1, "Пройдена!")
        elif spell_checker.error_counter < self.max_errors_count:
            grade = (self.max_errors_count - spell_checker.error_counter) / self.max_errors_count
        return answer(grade, feedback + spell_checker.get_format_result())


if __name__ == "__main__":
    from app.main.checker import check
    from app.main.parser import parse
    from app.db.db_types import Check

    original_filepath = 'app/report.docx'
    pdf_filepath = 'app/report.pdf'
    check_obj = Check(dict(criteria='VKRPack'))
    pack_obj = {
        "name": "VKRPack",
        "file_type": {
            "type": "report",
            "report_type": "VKR"
        },
        "min_score": 1,
        "raw_criterions": [
            [
            "spelling_check"
            ]
        ],
        "updated": {
            "$date": "2026-04-17T19:07:10.721Z"
        }
    }
    result = check(parse(original_filepath, pdf_filepath), check_obj, pack_obj=pack_obj)
    a = result.enabled_checks[0]['verdict']
    with open('report.html', 'w') as file:
        print(result.enabled_checks[0]['verdict'], file=file)
