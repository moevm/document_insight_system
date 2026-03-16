from ..base_check import BaseReportCriterion, answer

class ReportСhaptersLevel3ContentCheck(BaseReportCriterion):
    label = "Проверка содержания на наличия объктов 3 уровня"
    description = "В содержании не должно быть объектов третьего уровня"
    id = 'report_3_level_in_content_check'

    def __init__(self, file_info):
        super().__init__(file_info)


    def check(self):
        try:           
            headers = self.file.make_chapters(self.file_type['report_type'])
            
            if not headers:
                return answer(False, "Не найдено ни одного заголовка.")
            
            level_3_count = 0
            bool_content_find = False
            for header in headers:
                if header["text"].upper() == "СОДЕРЖАНИЕ":
                    bool_content_find = True
                    level_3_count = self._count_level_3_headers(header["child"])
                    break
            
            if not bool_content_find:
                return answer(False, "Не найдено заголовка 'Содержание'")

            if level_3_count > 0:
                result_str = f"Найдено {level_3_count} заголовков 3 уровня и выше. "
                result_str += "Содержание должно содержать только заголовки 1 и 2 уровня.<br>"
                return answer(False, result_str)
            
            return answer(True, "Все заголовки соответствуют требованиям (1-2 уровень)")
            
        except Exception as e:
            return answer(False, f"Ошибка при проверке: {str(e)}")
    
    def _count_level_3_headers(self, content):
        count = 0
        
        for header in content:
            if self._is_level_3_or_higher(header):
                count += 1
                count += self._count_level_3_headers(header["child"])
        
        return count
    
    def _is_level_3_or_higher(self, header):
        return header["level"] >= 3
