from language_tool_python import LanguageTool

from ..base_check import BaseReportCriterion, answer


class SpellingCheck(BaseReportCriterion):
    description = "Проверка наличия орфографических ошибок в тексте."
    id = 'spelling_check'

    # If it is, then errors_count is equal to the number of possible errors on 1 page 
    # (i.e. the maximum number of errors that can be allowed is errors_count*number_of_pages)
    # Else errors_count is equal to the maximum number of errors that can be allowed.
    def __init__(self, file_info, errors_count=4, scale_with_num_of_pages=True):
        super().__init__(file_info)
        self.spell_checker = LanguageTool('ru-RU')
        self.max_errors_count = errors_count
        if scale_with_num_of_pages:
            self.max_errors_count = errors_count * self.file.page_counter()
        else:
            self.max_errors_count = errors_count

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

        if len(possible_errors_list) < self.max_errors_count:
            return answer(True, "Пройдена!")
        else:
            result_str = '</li><li>'.join([error for error in possible_errors_list])
            return answer(False,
                          f'Найдены следующие ошибки написания (общее их число - {len(possible_errors_list)}): '
                          f'<ul><li>{result_str}</ul>')
