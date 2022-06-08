from app.main.mse22.checks.base_report_check import BaseReportCheck


class BannedWordsReportCheck(BaseReportCheck):
    def __init__(self, word_list):
        super().__init__()
        self.word_list = word_list

    def check(self, pages):
        for page in pages:
            for page_object in page.pageObjects:
                if page_object.type != "paragraph":
                    continue
                for word in self.word_list:
                    if page_object.text.lower().find(" " + word) != -1:
                        self.msg += f"\nСтрока \"{page_object.text}\": присутствует запрещённое слово \"{word}\""
                        self.succeeded = False
        return {"succeeded": self.succeeded, "message": self.msg}