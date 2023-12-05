import pymorphy2

morph = pymorphy2.MorphAnalyzer()


def answer(mod, *args):
    return {
        'score': float(mod),
        'verdict': args
    }


class BaseCriterion:
    description = None
    file_type = None
    id = None
    priority = False  # if priority criterion is failed -> check is failed

    def __init__(self, file_info):
        self.file = file_info.get('file')
        self.filename = file_info.get('filename', '')
        self.pdf_id = file_info.get('pdf_id')

    def check(self):
        raise NotImplementedError()

    def format_page_link(self, error):
        base_pdf_link = f'/get_pdf/{self.pdf_id}'
        page = lambda err: f'{base_pdf_link}#page={str(err)}'
        return [f'<a href="{page(e)}"target="_blank" rel="noopener">{str(e)}<a>' for e in error]

    @property
    def name(self):
        return self.description


class BasePresCriterion(BaseCriterion):
    file_type = 'pres'


class BaseReportCriterion(BaseCriterion):
    file_type = {'type': 'report', 'report_type': 'VKR'}
