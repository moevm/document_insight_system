from db.db_methods import get_criteria_pack

from .check_packs import BaseCriterionPack


def check(parsed_file, check_obj):
    filename = check_obj.filename
    file_info = {
        'file': parsed_file,
        'filename': filename,
        'pdf_id': check_obj.conv_pdf_fs_id
    }
    pack = BaseCriterionPack(**get_criteria_pack(check_obj.criteria))
    pack.init(file_info)
    result, score, is_passed = pack.check()

    check_obj.enabled_checks = result
    check_obj.score = score
    check_obj.is_passed = is_passed
    if check_obj.params_for_passback:
        check_obj.is_passbacked = False

    return check_obj
