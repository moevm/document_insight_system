from language_tool_python import LanguageTool

from ..base_check import BaseReportCriterion, answer


class SpellingCheck(BaseReportCriterion):
    description = "Проверка наличия орфографических ошибок в тексте."
    id = 'spelling_check'

    def __init__(self, file_info, min_errors_count=200, max_errors_count=400):
        super().__init__(file_info)
        self.spell_checker = LanguageTool('ru-RU')
        self.min_errors_count = min_errors_count
        self.max_errors_count = max_errors_count

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        possible_errors_list = []
        for page_num, text_on_page in enumerate(self.file.pdf_file.get_text_on_page().values()):
            possible_errors = self.spell_checker.check(text_on_page)
            for possible_error in possible_errors:
                if possible_error.ruleId == "MORFOLOGIK_RULE_RU_RU":
                    # Сохраняем только 2 предложения по замене.
                    replacements = possible_error.replacements[:2]
                    # Сохраняем контекст ошибки.
                    context = possible_error.context
                    possible_errors_list.append(
                        f"Ошибка находится на странице {str(page_num)}." +
                        f"Контекст ошибки: {context}" +
                        f"Возможные исправления: {replacements}"
                    )

        if len(possible_errors_list) <= self.min_errors_count:
            grade = 1
            return answer(1, "Пройдена!")
        elif len(possible_errors_list) < self.max_errors_count:
            grade = (self.max_errors_count - len(possible_errors_list)) / self.min_errors_count
            result_str = '</li><li>'.join([error for error in possible_errors_list])
            return answer(grade, 
                          f'Частично пройдена. '
                          f'Найдены следующие ошибки написания (общее их число - {len(possible_errors_list)}): '
                          f'<ul><li>{result_str}</ul>')
        else:
            result_str = '</li><li>'.join([error for error in possible_errors_list])
            return answer(0,
                          f'Найдены следующие ошибки написания (общее их число - {len(possible_errors_list)}): '
                          f'<ul><li>{result_str}</ul>')
