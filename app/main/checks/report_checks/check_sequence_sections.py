
from ..base_check import BaseReportCriterion, answer


class ReportSequenceSectionsCheck(BaseReportCriterion):
    label = "Проверка последовательности разделов"
    description = "Структура работы не правильна: до раздела 'ВВЕДЕНИЕ' должны быть в определенном порядке разделы:" \
    "'ЗАДАНИЕ НА ВЫПУСКНУЮ КВАЛИФИКАЦИОННУЮ РАБОТУ' (заголовок первого уровня)" \
    "'КАЛЕНДАРНЫЙ ПЛАН ВЫПОЛНЕНИЯ ВЫПУСКНОЙ КВАЛИФИКАЦИОННОЙ РАБОТЫ' (заголовок первого уровня)" \
    "'РЕФЕРАТ' (заголовок первого уровня)" \
    "'ABSTRACT' (заголовок первого уровня)" \
    "'СОДЕРЖАНИЕ' (заголовок второго уровня)" \
    " 'ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ' (заголовок второго уровня)"
    id = 'report_sequence_sections_check'

    def __init__(self, file_info):
        super().__init__(file_info)

    def check(self):
        try:
            headers = self.file.make_chapters(self.file_type['report_type'])
            # return answer(True, f"{headers}")
            if not headers:
                return answer(False, "Не найдено ни одного заголовка.")

            flag_intro, struct_label = get_header_1_2_level(headers, [])

            if not flag_intro:
                return answer(False, "Не найдено раздела 'ВВЕДЕНИЕ'/'ВСТУПЛЕНИЕ'")

            if " ".join(struct_label) != "ЗАДАНИЕ НА ВЫПУСКНУЮ КВАЛИФИКАЦИОННУЮ РАБОТУ КАЛЕНДАРНЫЙ ПЛАН ВЫПОЛНЕНИЯ ВЫПУСКНОЙ КВАЛИФИКАЦИОННОЙ РАБОТЫ" \
            " РЕФЕРАТ ABSTRACT СОДЕРЖАНИЕ ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ":
                return answer(False, f"Ваша структура работы не соотвествует требуемой: {'\n'.join(struct_label)}")
                

            return answer(True, "Проверка последовательности разделов до раздела 'ВВЕДЕНИЕ' пройдена")

        except Exception as e:
            return answer(False, f"Ошибка про проверке последовательности разделов до раздела 'ВВЕДЕНИЕ'/'ВСТУПЛЕНИЕ': {str(e)}, {self.file.make_chapters(self.file_type['report_type'])}")


def get_header_1_2_level(headers, struct_label):
    for header in headers:
        style = header.get('style', '').lower()
        
        if style != "heading 1" and style != "heading 2" :
            continue

        name_label = header['text'].strip().upper()
        
        if name_label in ["ВВЕДЕНИЕ", "ВСТУПЛЕНИЕ"]:
            return True, struct_label
        
        struct_label.append(name_label.upper())
    
    return False, struct_label
