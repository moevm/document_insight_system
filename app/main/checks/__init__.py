from .presentation_checks import *
from .report_checks import *
from .report_checks.sections_check import ReportSectionCheck
from .report_checks.headers_at_page_top_check import ReportHeadersAtPageTopCheck
from .report_checks.style_check import ReportStyleCheck


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
        ReportShortSectionsCheck.id: ReportShortSectionsCheck,
        ReportStyleCheck.id: ReportStyleCheck,
        ReportBannedWordsCheck.id: ReportBannedWordsCheck,
        ReportRightWordsCheck.id: ReportRightWordsCheck,
        BannedWordsInLiteratureCheck.id: BannedWordsInLiteratureCheck,
        ReferencesToLiteratureCheck.id: ReferencesToLiteratureCheck,
        ReportNeededPages.id: ReportNeededPages,
        ReportNeededHeaders.id: ReportNeededHeaders,
        ReportHeaders.id: ReportHeaders,
        ReportIntroduction.id: ReportIntroduction,
        ReportMainTextCheck.id: ReportMainTextCheck

    }
}
