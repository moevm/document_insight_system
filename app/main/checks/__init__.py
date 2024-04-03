import inspect
from .presentation_checks import *
from .report_checks import *
from .base_check import BaseCriterion

classes_pres = filter(
    lambda member: inspect.isclass(member[1]) and issubclass(member[1], BaseCriterion) and hasattr(member[1], 'id'),
    inspect.getmembers(presentation_checks)
    )
classes_report = filter(
    lambda member: inspect.isclass(member[1]) and issubclass(member[1], BaseCriterion) and hasattr(member[1], 'id'),
    inspect.getmembers(report_checks)
    )

CRITERIA_INFO = {
    'pres': {cls.id: {'class': cls, 'name': name, 'label': cls.label, 'description': cls.description} for name, cls in classes_pres},
    'report': {cls.id: {'class': cls, 'name': name, 'label': cls.label, 'description': cls.description} for name, cls in classes_report}
}

AVAILABLE_CHECKS = {
    'pres': {cls_id: CRITERIA_INFO['pres'][cls_id]['class'] for cls_id in CRITERIA_INFO['pres']},
    'report': {cls_id: CRITERIA_INFO['report'][cls_id]['class'] for cls_id in CRITERIA_INFO['report']}
}
