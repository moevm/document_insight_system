from flask import Blueprint, request, redirect, url_for, abort
from flask_login import logout_user, login_user

from app.lti_session_passback.lti import utils
from app.lti_session_passback.lti.check_request import check_request
from app.main.check_packs import BASE_PACKS, BaseCriterionPack, DEFAULT_TYPE
from app.root_logger import get_root_logger
from app.db.methods import user as user_methods
from app.db.methods.edit_user import edit_user
from app.db.methods import criteria_pack as criteria_pack_methods

from app.server_consts import ALLOWED_EXTENSIONS

lti = Blueprint('lti', __name__, template_folder='templates', static_folder='static')
logger = get_root_logger('web')


@lti.route('/lti', methods=['POST'])
def lti_main():
    if check_request(request):
        temporary_user_params = request.form
        username = temporary_user_params.get('ext_user_username')
        person_name = utils.get_person_name(temporary_user_params)
        user_id = f"{username}_{temporary_user_params.get('tool_consumer_instance_guid', '')}"
        lms_user_id = temporary_user_params.get('user_id', '')
        params_for_passback = utils.extract_passback_params(temporary_user_params)
        custom_params = utils.get_custom_params(temporary_user_params)

        # task settings
        # pack name
        custom_criterion_pack = custom_params.get('pack', BASE_PACKS.get(DEFAULT_TYPE).name)
        criterion_pack_info = criteria_pack_methods.get_criteria_pack(custom_criterion_pack)
        if not criterion_pack_info:
            default_criterion_pack = BASE_PACKS.get(DEFAULT_TYPE).name
            logger.error(
                f"Ошибка при lti-авторизации. Несуществующий набор {custom_criterion_pack} пользователя {username}. Установлен набор по умолчанию: {default_criterion_pack}")
            logger.debug(f"lti-параметры: {temporary_user_params}")
            custom_criterion_pack = default_criterion_pack
            criterion_pack_info = criteria_pack_methods.get_criteria_pack(custom_criterion_pack)
        custom_criterion_pack_obj = BaseCriterionPack(**criterion_pack_info)
        # get file type and formats from pack
        file_type_info = custom_criterion_pack_obj.file_type
        file_type = file_type_info['type']
        two_files = bool(custom_params.get('two_files'))
        formats = sorted((set(map(str.lower, custom_params.get('formats', '').split(','))) & ALLOWED_EXTENSIONS[
            file_type] or ALLOWED_EXTENSIONS[file_type]))

        role = utils.get_role(temporary_user_params)

        logout_user()

        lti_user = user_methods.add_user(user_id, is_LTI=True)
        if lti_user:
            lti_user.name = person_name
            lti_user.is_admin = role
        else:
            lti_user = user_methods.get_user(user_id)

        # task settings
        lti_user.file_type = file_type_info
        lti_user.two_files = two_files
        lti_user.formats = formats
        lti_user.criteria = custom_criterion_pack
        # passback settings
        lti_user.params_for_passback = params_for_passback
        lti_user.lms_user_id = lms_user_id

        edit_user(lti_user)

        login_user(lti_user)
        return redirect(url_for('upload'))
    else:
        abort(403)
        