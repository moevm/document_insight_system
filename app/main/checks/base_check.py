import pymorphy3

morph = pymorphy3.MorphAnalyzer()


def answer(mod, *args):
    return {
        'score': float(mod),
        'verdict': args
    }


class BaseCriterion:
    _description = None
    label = None
    id = None
    priority = False    # if priority criterion is failed -> check is failed
    warning = False     # warning priority doesn't effect to result score

    def __init__(self, file_info):
        self.file = file_info.get('file')
        self.filename = file_info.get('filename', '')
        self.pdf_id = file_info.get('pdf_id')
        self.file_type = file_info.get('file_type')

    def check(self):
        raise NotImplementedError()

    def format_page_link(self, error):
        base_pdf_link = f'/get_pdf/{self.pdf_id}'
        page = lambda err: f'{base_pdf_link}#page={str(err)}'
        return [f'<a href="{page(e)}"target="_blank" rel="noopener">{str(e)}<a>' for e in error]
    
    @classmethod    # TODO: criteria can depend on params (from db) 
    def description(cls, pack: str | None = None):
        return cls._description

    @property
    def name(self):
        return self.label


class BasePresCriterion(BaseCriterion):
    pass


class BaseReportCriterion(BaseCriterion):
    pass