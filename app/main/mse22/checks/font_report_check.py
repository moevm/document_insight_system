from app.main.mse22.checks.base_report_check import BaseReportCheck
from app.main.mse22.criteria.maintext import MainText


class FontReportCheck(BaseReportCheck):
    def __init__(self, criteria):
        super().__init__()
        self.criteria = criteria

    def check(self, pages):
        for page in pages[1:]:
            main_text = MainText(page.pageObjects[1:], self.criteria)
            self.succeeded &= main_text.get_output()
            self.msg += main_text.msg
        return {"succeeded": self.succeeded, "message": self.msg}
