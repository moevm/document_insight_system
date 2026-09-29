import re
from ..base_check import BaseReportCriterion, answer


class AntiPlagiarismCheck(BaseReportCriterion):
    label = "Проверка на заимствования"
    _description = ''
    id = 'anti_plagiarism_check'

    def __init__(self, file_info, originality_threshold=70):
        super().__init__(file_info)
        self.chapters = []
        self.originality_threshold = originality_threshold

    def late_init(self):
        self.chapters = self.file.make_chapters(self.file_type['report_type'])

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        self.late_init()
        text = ""
        user_result_str = ""
        for chapter in self.chapters:
            if 'список использованных источников' in chapter['text'].lower():
                break
            for child in chapter['child']:
                text += " " + child['text'] # заменить на нужную для метода шинглов структуру
        result = self.run_antiplagiarism(text)
        originality_percent = result["originality"]
        borrowed_fragments = result["fragments"]
        if originality_percent < self.originality_threshold:
            user_result_str += f"Обнаружены заимствования в тексте отчета. Уникальность работы составляет {originality_percent}%.<br>"
            admin_result_str = user_result_str
            admin_result_str += f"Ниже приведены фраменты, содержащие заимстования.<br><br>"
            for i, fragment in enumerate(borrowed_fragments, start=1):
                source_check_id = str(fragment.get('source', ''))
                admin_result_str += (f"Заимствованный фрагмент №{i} находится на странице {fragment['page_in_doc']}. "
                    f"Источник: {fragment['source']}, страница {fragment['page_in_source']}."
                    f"Совпадение {fragment['percent']}%<br>"
                    f"Текст фрагмента:<br>"
                    f"{fragment['text']}<br>"
                    f"Подробнее: <a href=\"#\" target=\"_blank\" "
                    f"onclick=\"const antiPath = window.location.pathname.replace('/results/', '/anti_plagiarism/');"
                    f"window.open(`${{antiPath}}/{source_check_id}`, '_blank'); return false;\">"
                    f"перейти к сравнению</a><br><br>"
                )
            return answer(False, user_result_str, admin_result_str)
        return answer(True, f"Уникальность текста {originality_percent}%. Проверка пройдена.")

    def run_antiplagiarism(self, text):
        # вызов реального алгоритма антиплагиата
        originality = 65
        fragments = [
            {
                "text": "пример заимствованного текста",
                "source": "doc_id",
                "percent": 90,
                "page_in_doc": 5,
                "page_in_source": 8
                
            },
            {
                "text": "еще один заимствованный фрагмент",
                "source": "doc_id2",
                "percent": 70,
                "page_in_doc": 7,
                "page_in_source": 9
            }
        ]

        return {
            "originality": originality,
            "fragments": fragments
        }
