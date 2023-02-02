import traceback
from logging import getLogger

from ..checks import AVAILABLE_CHECKS

logger = getLogger('root_logger')


def init_criterions(criterions, file_type, file_info={}):
    """
    criterions = [[criterion_id, criterion_params], ...]  # criterion_params is dict
    """
    try:
        existing_criterions = AVAILABLE_CHECKS.get(file_type['type'], {})
        errors = []
        initialized_checks = []
        for criterion in criterions:
            criterion_id = criterion[0]
            criterion_params = criterion[1] if len(criterion) == 2 else {}  # criterion settings may contain only id
            if criterion_id not in existing_criterions:
                errors.append(
                    f"Неизвестный критерий '{criterion_id}' для типа файла '{file_type}' с параметрами {criterion_params}.")
                continue

            criterion_obj = None
            try:
                criterion_obj = existing_criterions[criterion_id](file_info=file_info, **criterion_params)
            except Exception as exc:
                err_msg = f"Ошибка при формировании '{criterion_id}' с параметрами {criterion_params}. Полная ошибка: {exc}"
                errors.append(err_msg)
                logger.warning(f"{err_msg}. {traceback.format_exc()}")

            if criterion_obj: initialized_checks.append(criterion_obj)
    except Exception as exc:
        initialized_checks, errors = [], [f"Ошибка при обработке конфигурации '{exc}'."]
        logger.error(traceback.format_exc())
    return initialized_checks, errors
