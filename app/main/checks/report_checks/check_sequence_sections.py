
from ..base_check import BaseReportCriterion, answer


class ReportSequenceSectionsCheck(BaseReportCriterion):
    label = "Проверка последовательности разделов"
    description = "Структура работы не правильна: до раздела 'ВВЕДЕНИЕ' должны быть только титульник и раздел 'СОДЕРЖАНИЕ'/'ОГЛАВЛЕНИЕ'."
    id = 'report_sequence_sections_check'

    def __init__(self, file_info):
        super().__init__(file_info)

    def check(self):
        try:           
            headers = self.file.make_chapters(self.file_type['report_type'])
            
            if not headers:
                return answer(False, "Не найдено ни одного заголовка.")

            struct_label = []
            flag_intro = False
            for header in headers:
                name_label = header['text']

                if header["style"] != 'heading 1':
                    continue

                if name_label.upper() == "ВВЕДЕНИЕ" or name_label.upper() == "ВСТУПЛЕНИЕ":
                    flag_intro = True
                    break

                struct_label.append(name_label.upper())

            if not flag_intro:
                return answer(False, "Не найдено раздела 'ВВЕДЕНИЕ'/'ВСТУПЛЕНИЕ' (1 уровень загаловка)")

            if len(struct_label) == 1 and (struct_label[0] == "ОГЛАВЛЕНИЕ" or struct_label[0] == "СОДЕРЖАНИЕ"):
                return answer(True, "Проверка последовательности разделов до раздела 'ВВЕДЕНИЕ' пройдена")

            return answer(False, f"Найдены лишние разделы 1-ого уровня до раздела 'ВВЕДЕНИЕ'/'ВСТУПЛЕНИЕ': {' '.join(struct_label)}")


        except Exception as e:
            return answer(False, f"Ошибка про проверке последовательности разделов до раздела 'ВВЕДЕНИЕ'/'ВСТУПЛЕНИЕ': {str(e)}, {self.file.make_chapters(self.file_type['report_type'])}")
        