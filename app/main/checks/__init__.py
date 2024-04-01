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

AVAILABLE_CHECKS = {
    'pres': {cls.id: cls for _, cls in classes_pres},
    'report': {cls.id: cls for _, cls in classes_report}
}

print(AVAILABLE_CHECKS)
