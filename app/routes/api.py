import json
import bson
from bson import ObjectId

from flask import Blueprint, abort, request
from flask_login import login_required, current_user

from datetime import datetime
from app.db.methods import check as check_methods
from app.db.methods import criteria_pack as criteria_pack_methods
from app.root_logger import get_root_logger
from app.main.check_packs import BASE_PACKS, DEFAULT_REPORT_TYPE_INFO, REPORT_TYPES, init_criterions


api = Blueprint('api', __name__, template_folder='templates', static_folder='static')
logger = get_root_logger('web')


@api.route("/results/ready/<string:_id>", methods=["GET"])
def ready_result(_id):
    try:
        oid = ObjectId(_id)
    except bson.errors.InvalidId:
        logger.error('_id exception:', exc_info=True)
        return {}
    check = check_methods.get_check(oid)
    if check is not None:
        return {"is_ended": check.is_ended}


@api.route("/criterion_pack", methods=["POST"])
@login_required
def api_criteria_pack():
    if not current_user.is_admin:
        abort(403)
    form_data = dict(request.form)
    pack_name = form_data.get('pack_name')
    # get pack configuration info
    raw_criterions = form_data.get('raw_criterions')
    file_type = form_data.get('file_type')
    report_type = form_data.get('report_type')
    min_score = float(form_data.get('min_score', '1'))
    # weak validation
    try:
        raw_criterions = json.loads(raw_criterions)
    except:
        msg = f"Ошибка при парсинге критериев {raw_criterions} для набора {pack_name} от пользователя {current_user.name}"
        logger.info(msg)
        return msg, 400
    raw_criterions = raw_criterions if type(raw_criterions) is list else None
    file_type = file_type if file_type in BASE_PACKS.keys() else None
    min_score = min_score if min_score and (0 <= min_score <= 1) else None
    if not (raw_criterions and file_type and min_score):
        msg = f"Конфигурация набора критериев должна содержать список критериев (непустой список в формате JSON)," \
              f"тип файла (один из {list(BASE_PACKS.keys())})," \
              f"пороговый балл (0<=x<=1). Получено: {form_data}, после обработки: file_type - {file_type}," \
              f"min_score - {min_score}, raw_criterions - {raw_criterions}"
        return {'data': msg, 'time': datetime.now()}, 400
    #  testing pack initialization
    file_type_info = {'type': file_type}
    if file_type == DEFAULT_REPORT_TYPE_INFO['type']:
        file_type_info['report_type'] = report_type if report_type in REPORT_TYPES else DEFAULT_REPORT_TYPE_INFO[
            'report_type']
    inited, err = init_criterions(raw_criterions, file_type=file_type_info)
    if len(raw_criterions) != len(inited) or err:
        msg = f"При инициализации набора {pack_name} возникли ошибки. JSON-конфигурация: '{raw_criterions}'. Успешно инициализированные: {inited}. Возникшие ошибки: {err}."
        return {'data': msg, 'time': datetime.now()}, 400
    # if ok - save to DB
    criteria_pack_methods.save_criteria_pack({
        'name': pack_name,
        'raw_criterions': raw_criterions,
        'file_type': file_type_info,
        'min_score': min_score
    })
    return {'data': f"Набор '{pack_name}' сохранен", 'time': datetime.now()}, 200
