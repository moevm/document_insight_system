from .presentation_checks import *
from .report_checks import *


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
        ReportNumberOfPages.id: ReportNumberOfPages,
        ReportImageShareCheck.id: ReportImageShareCheck,
        ReportSectionCheck.id: ReportSectionCheck,
        ReportHeadersAtPageTopCheck.id: ReportHeadersAtPageTopCheck,
        ReportBannedWordsCheck.id: ReportBannedWordsCheck,
        ReportRightWordsCheck.id: ReportRightWordsCheck,
        BannedWordsInLiteratureCheck.id: BannedWordsInLiteratureCheck
    }
}
