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

CLASSES_INFO = {
    'pres': {cls.id: (cls, cls.label, cls.description) for _, cls in classes_pres},
    'report': {cls.id: (cls, cls.label, cls.description) for _, cls in classes_report}
}

AVAILABLE_CHECKS = {
    'pres': {cls_id: cls for cls_id, (cls, _, _) in CLASSES_INFO['pres'].items()},
    'report': {cls_id: cls for cls_id, (cls, _, _) in CLASSES_INFO['report'].items()}
}

CRITERIA_INFO = {
        **{cls_id: {'label': cls_lbl, 'description': cls_desc} for cls_id, (_, cls_lbl, cls_desc) in CLASSES_INFO['pres'].items()},
        **{cls_id: {'label': cls_lbl, 'description': cls_desc} for cls_id, (_, cls_lbl, cls_desc) in CLASSES_INFO['report'].items()}
        }
