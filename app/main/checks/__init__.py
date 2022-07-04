from .presentation_checks import *
from .report_checks import *
from .report_checks.sections_check import ReportSectionCheck
from .report_checks.headers_at_page_top_check import ReportHeadersAtPageTopCheck

AVAILABLE_CHECKS = {
    'pres': {
        TemplateNameCheck.id: TemplateNameCheck,
        SldNumCheck.id: SldNumCheck,
        SldEnumCheck.id: SldEnumCheck,
        TitleFormatCheck.id: TitleFormatCheck,
        FindDefSld.id: FindDefSld,
        SearchKeyWord.id: SearchKeyWord,
        FindTasks.id: FindTasks,
        SldSimilarity.id: SldSimilarity,
        FurtherDev.id: FurtherDev
    },
    'report': {
        ReportSimpleCheck.id: ReportSimpleCheck,
        ReportSectionCheck.id: ReportSectionCheck,
        ReportBannedWordsCheck.id: ReportBannedWordsCheck,
        ReportHeadersAtPageTopCheck.id: ReportHeadersAtPageTopCheck
    }
}
