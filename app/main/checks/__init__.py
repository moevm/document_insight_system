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
        PresRightWordsCheck.id: PresRightWordsCheck,
        PresImageShareCheck.id: PresImageShareCheck,
        FurtherDev.id: FurtherDev,
        PresBannedWordsCheck.id: PresBannedWordsCheck,
        PresEmptySlideCheck.id: PresEmptySlideCheck,
    },
    'report': {
        ReportSimpleCheck.id: ReportSimpleCheck,
        ReportPageCounter.id: ReportPageCounter,
        ReportImageShareCheck.id: ReportImageShareCheck,
        LRReportSectionCheck.id: LRReportSectionCheck,
        ReportHeadersAtPageTopCheck.id: ReportHeadersAtPageTopCheck,
        ReportShortSectionsCheck.id: ReportShortSectionsCheck,
        ReportStyleCheck.id: ReportStyleCheck,
        ReportBannedWordsCheck.id: ReportBannedWordsCheck,
        ReportRightWordsCheck.id: ReportRightWordsCheck,
        BannedWordsInLiteratureCheck.id: BannedWordsInLiteratureCheck,
        ReferencesToLiteratureCheck.id: ReferencesToLiteratureCheck,
        ImageReferences.id: ImageReferences,
        TableReferences.id: TableReferences,
        ReportFirstPagesCheck.id: ReportFirstPagesCheck,
        ReportMainCharacterCheck.id: ReportMainCharacterCheck,
        ReportNeededHeadersCheck.id: ReportNeededHeadersCheck,
        ReportChapters.id: ReportChapters,
        ReportSectionComponent.id: ReportSectionComponent,
        ReportMainTextCheck.id: ReportMainTextCheck,
        SpellingCheck.id: SpellingCheck
    }
}
