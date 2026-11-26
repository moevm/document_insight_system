import json
import traceback
from logging import getLogger

from ..checks import AVAILABLE_CHECKS
from ..checks.base_check import BaseCriterion, answer


class FailedCriterion(BaseCriterion):
    priority = True
    label = "Ошибка настройки критерия"

    def __init__(self, file_info, criterion_id, error):
        super().__init__(file_info)
        self.id = criterion_id
        self.error = error

    def check(self):
        return answer(0, self.error)


logger = getLogger('root_logger')


def init_criterions(criterions, file_info):
    """
    criterions = [[criterion_id, criterion_params], ...]  # criterion_params is dict
    """
    try:
        file_type = file_info['file_type']
        existing_criterions = AVAILABLE_CHECKS.get(file_type['type'], {})
        errors = []
        initialized_checks = []
        seen = set()
        if not isinstance(criterions, (list, tuple)):
            raise ValueError('Набор критериев должен быть списком.')
        for criterion in criterions:
            if (
                not isinstance(criterion, (list, tuple))
                or not 1 <= len(criterion) <= 2
                or not isinstance(criterion[0], str)
                or (len(criterion) == 2 and not isinstance(criterion[1], dict))
            ):
                error = f'Некорректная запись критерия: {criterion!r}'
                errors.append(error)
                initialized_checks.append(FailedCriterion(file_info, 'invalid_criterion', error))
                continue
            criterion_id = criterion[0]
            criterion_params = criterion[1] if len(criterion) == 2 else {}
            signature = json.dumps([criterion_id, criterion_params], sort_keys=True, ensure_ascii=False)
            if signature in seen:
                continue
            seen.add(signature)
            if criterion_id not in existing_criterions:
                errors.append(
                    f"Неизвестный критерий '{criterion_id}' для типа файла "
                    f"'{file_type}' с параметрами {criterion_params}."
                )
                initialized_checks.append(FailedCriterion(file_info, criterion_id, errors[-1]))
                continue

            criterion_obj = None
            try:
                criterion_obj = existing_criterions[criterion_id](file_info=file_info, **criterion_params)
            except Exception as exc:
                err_msg = (
                    f"Ошибка при формировании '{criterion_id}' с параметрами {criterion_params}. Полная ошибка: {exc}"
                )
                errors.append(err_msg)
                logger.warning(f"{err_msg}. {traceback.format_exc()}")
                initialized_checks.append(FailedCriterion(file_info, criterion_id, err_msg))

            if criterion_obj:
                initialized_checks.append(criterion_obj)
    except Exception as exc:
        errors = [f"Ошибка при обработке конфигурации '{exc}'."]
        initialized_checks = [FailedCriterion(file_info, 'invalid_criterion_pack', errors[0])]
        logger.error(traceback.format_exc())
    return initialized_checks, errors
