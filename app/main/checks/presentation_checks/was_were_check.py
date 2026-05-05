from ..base_check import BasePresCriterion, answer
from app.utils.was_were_check import WasWereChecker


class PresWasWereCheck(BasePresCriterion):
    label = "Проверка на пассивные конструкции, начинающиеся с Был/Была/Было/Были, которые можно убрать без потери смысла"
    id = "pres_was_were_check"

    def __init__(self, file_info, threshold=3):
        super().__init__(file_info)
        self.threshold = threshold
        self.checker = WasWereChecker(file_info, threshold)

    def check(self):
        message, score = self.checker.get_result_msg_and_score(
            self.file, self.format_page_link
        )
        return answer(score, message)
