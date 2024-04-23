import inspect
from . import presentation_checks, report_checks
from .base_check import BaseCriterion


def get_filtered_module_members(module):
    return filter(
        lambda member: inspect.isclass(member[1]) and issubclass(member[1], BaseCriterion),
        inspect.getmembers(module)
    )


CRITERIA_INFO = {
    'pres': {cls.id: {'class': cls, 'name': name, 'label': cls.label, 'description': cls.description} for name, cls in get_filtered_module_members(presentation_checks)},
    'report': {cls.id: {'class': cls, 'name': name, 'label': cls.label, 'description': cls.description} for name, cls in get_filtered_module_members(report_checks)}
}

AVAILABLE_CHECKS = {
    'pres': {cls_id: CRITERIA_INFO['pres'][cls_id]['class'] for cls_id in CRITERIA_INFO['pres']},
    'report': {cls_id: CRITERIA_INFO['report'][cls_id]['class'] for cls_id in CRITERIA_INFO['report']}
}
