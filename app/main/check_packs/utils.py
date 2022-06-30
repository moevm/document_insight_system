from ..checks import AVAILABLE_CHECKS


def init_criterions(criterions, file_info=None, file_type='pres'):
    """
    criterions = ((criterion_id, criterion_params), ...)  # criterion_params is dict
    """
    existing_criterions = AVAILABLE_CHECKS.get(file_type, {})
    errors = []
    initialized_checks = []

    for criterion_id, criterion_params in criterions:
        if criterion_id not in existing_criterions:
            errors.append(f"Неизвестный критерий '{criterion_id}' с параметрами {criterion_params}.")
            continue

        criterion_obj = None
        try:
            criterion_obj = existing_criterions[criterion_id](file_info=file_info, **criterion_params)
        except Exception as exc:
            errors.append(
                f"Ошибка при формировании '{criterion_id}' с параметрами {criterion_params}. Полная ошибка: {exc}")

        if criterion_obj: initialized_checks.append(criterion_obj)

    return initialized_checks, errors
