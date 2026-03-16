from .._dynamic_import import setup_dynamic_import
from ..base_check import BaseCriterion


__all__ = setup_dynamic_import(
    module_globals=globals(),
    base_class=BaseCriterion,
    current_file=__file__
)