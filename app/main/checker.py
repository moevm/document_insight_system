from db.db_methods import get_criteria_pack
from .check_packs import BaseCriterionPack


def check(parsed_file, check_obj, filename, user):
    file_info = {
        'file': parsed_file,
        'filename': filename,
        'pdf_id': check_obj.conv_pdf_fs_id
    }
    pack = BaseCriterionPack(**get_criteria_pack(user.enabled_checks))
    pack.init(file_info)
    result, score, is_passed = pack.check()

    check_obj.enabled_checks = result
    check_obj.score = score
    check_obj.is_passed = is_passed
    check_obj.filename = filename
    check_obj.user = user.username
    check_obj.lms_user_id = user.lms_user_id
    if user.params_for_passback:
        check_obj.is_passbacked = False

    return check_obj
