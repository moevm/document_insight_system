from ..base_check import BaseReportCriterion, answer


class ReportMaxSizeOfAbstractCheck(BaseReportCriterion):
    description = "Максимальный размер раздела Реферат в ВКР"
    id = "max_abstract_size_check"

    def __init__(self, file_info):
        super().__init__(file_info)

    def check(self):
        return answer(True, "123123")