from db.db_methods import get_criteria_pack

from .check_packs import BaseCriterionPack

mock_check_result = [dict(id='simple_check', name="Проверка валидности файла при парсинге", score=0,
                          verdict=[
                              "При обработке загруженного исходного файла возникла ошибка.<br>Попробуйте пересохранить файл (например, с помощью другого редактора).<br>В случае, если ситуация не изменится - свяжитесь по почте с dmitry.ivanov@moevm.info"])], 0, False


def check(parsed_file, check_obj):
    if parsed_file:
        # parsed_file is not None
        filename = check_obj.filename
        file_info = {
            'file': parsed_file,
            'filename': filename,
            'pdf_id': check_obj.conv_pdf_fs_id
        }
        pack = BaseCriterionPack(**get_criteria_pack(check_obj.criteria))
        pack.init(file_info)
        result, score, is_passed = pack.check()
    else:
        result, score, is_passed = mock_check_result

    check_obj.enabled_checks = result
    check_obj.score = score
    check_obj.is_passed = is_passed
    if check_obj.params_for_passback:
        check_obj.is_passbacked = False

    return check_obj
