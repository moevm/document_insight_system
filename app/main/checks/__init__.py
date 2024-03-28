import inspect
from .presentation_checks import *
from .report_checks import *

members_pres = inspect.getmembers(presentation_checks)
classes_pres = [member[1] for member in members_pres if inspect.isclass(member[1])]
members_report = inspect.getmembers(report_checks)
classes_report = [member[1] for member in members_report if inspect.isclass(member[1])]

AVAILABLE_CHECKS = {
    'pres': {cls.id: cls for cls in classes_pres if hasattr(cls, 'id')},
    'report': {cls.id: cls for cls in classes_report if hasattr(cls, 'id')}
}

# AVAILABLE_CHECKS = {
#     'pres': {
#         TemplateNameCheck.id: TemplateNameCheck,
#         SldNumCheck.id: SldNumCheck,
#         SldEnumCheck.id: SldEnumCheck,
#         TitleFormatCheck.id: TitleFormatCheck,
#         FindDefSld.id: FindDefSld,
#         SearchKeyWord.id: SearchKeyWord,
#         FindTasks.id: FindTasks,
#         SldSimilarity.id: SldSimilarity,
#         PresRightWordsCheck.id: PresRightWordsCheck,
#         PresImageShareCheck.id: PresImageShareCheck,
#         FurtherDev.id: FurtherDev,
#         PresBannedWordsCheck.id: PresBannedWordsCheck,
#         PresVerifyGitLinkCheck.id: PresVerifyGitLinkCheck,
#         PresEmptySlideCheck.id: PresEmptySlideCheck,
#     },
#     'report': {
#         ReportSimpleCheck.id: ReportSimpleCheck,
#         ReportPageCounter.id: ReportPageCounter,
#         ReportImageShareCheck.id: ReportImageShareCheck,
#         LRReportSectionCheck.id: LRReportSectionCheck,
#         ReportHeadersAtPageTopCheck.id: ReportHeadersAtPageTopCheck,
#         ReportShortSectionsCheck.id: ReportShortSectionsCheck,
#         ReportStyleCheck.id: ReportStyleCheck,
#         ReportBannedWordsCheck.id: ReportBannedWordsCheck,
#         ReportRightWordsCheck.id: ReportRightWordsCheck,
#         BannedWordsInLiteratureCheck.id: BannedWordsInLiteratureCheck,
#         ReferencesToLiteratureCheck.id: ReferencesToLiteratureCheck,
#         ImageReferences.id: ImageReferences,
#         TableReferences.id: TableReferences,
#         ReportFirstPagesCheck.id: ReportFirstPagesCheck,
#         ReportMainCharacterCheck.id: ReportMainCharacterCheck,
#         ReportNeededHeadersCheck.id: ReportNeededHeadersCheck,
#         ReportChapters.id: ReportChapters,
#         ReportSectionComponent.id: ReportSectionComponent,
#         ReportMainTextCheck.id: ReportMainTextCheck,
#         SpellingCheck.id: SpellingCheck
#     }
# }



