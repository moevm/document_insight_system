from .presentation_checks import *
from .report_checks import *
<<<<<<< HEAD
from .report_checks.sections_check import ReportSectionCheck
from .report_checks.headers_at_page_top_check import ReportHeadersAtPageTopCheck
from .report_checks.short_sections_check import ReportShortSectionsCheck
=======

>>>>>>> 302_check_sections

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
<<<<<<< HEAD
        ReportHeadersAtPageTopCheck.id: ReportHeadersAtPageTopCheck,
        ReportShortSectionsCheck.id: ReportShortSectionsCheck
=======
        ReportRightWordsCheck.id: ReportRightWordsCheck,
        BannedWordsInLiteratureCheck.id: BannedWordsInLiteratureCheck
>>>>>>> 302_check_sections
    }
}
