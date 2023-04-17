from app.db.db_types import Check


class Version:
    VERSION_NAME = '0.1'
    CHANGES = ""

    @classmethod
    def update_database(cls, collections, prev_version):
        """
        <collections> must contains (objects from pymongo)
        - users
        - presentations
        - checks
        - criteria_pack
        """
        raise NotImplementedError()

    @classmethod
    def to_dict(cls):
        return dict(
            version=cls.VERSION_NAME,
            changes=cls.CHANGES
        )


class Version10(Version):
    VERSION_NAME = '1.0'
    CHANGES = "Начальная версия БД (до https://github.com/moevm/mse_auto_checking_slides_vaganov/pull/110)"

    @classmethod
    def update_database(cls, collections, prev_version):
        pass


class Version11(Version):
    VERSION_NAME = '1.1'
    CHANGES = "В коллекцию checks добавлены поля filename, user и score. " \
              "Для перехода с версии 1.0 необходимо заполнить поля"

    @classmethod
    def update_database(cls, collections, prev_version):
        if prev_version == Version10.VERSION_NAME:
            collections['checks'].update({}, {
                '$set': {
                    'filename': '_.pptx',
                    'user': 'moevm',
                    'score': -1
                }
            })
        else:
            raise Exception(f'Неподдерживаемый переход с версии {prev_version}')


class Version20(Version):
    VERSION_NAME = '2.0'
    CHANGES = "Изменен подход к версионированию БД: исправляются минусы предыдущих версий " \
              "(поля filename/user/score заполняются верными значениями).\n" \
              "Также в критерий на количество слайдов добавлена нижняя граница. " \
              "Для перехода с версии 1.1 и ниже необходимо изменить значения поля criteria.slides_number у users " \
              "в зависимости от выбранных опций: 12 -> [10, 12], 15 -> [13, 15].\n" \
              "Для всех результатов проверок вводится поле 'verdict', содержащее подробное описание проверки."

    @classmethod
    def update_database(cls, collections, prev_version):
        if prev_version in (Version10.VERSION_NAME, Version11.VERSION_NAME):
            # process all checks of pres and set filename + user
            for presentation in collections['presentations'].find({}):
                filename = presentation['name']
                user_doc = collections['users'].find_one({'presentations': presentation['_id']})
                user = user_doc.get('username', 'moevm') if user_doc else 'moevm'
                for check_id in presentation["checks"]:
                    collections['checks'].update(
                        {"_id": check_id},
                        {'$set': {'filename': filename, 'user': user}}
                    )

            # if we have checks without presentation == after prev loop it doesn't include filename/user field
            # set default user='moevm', filename='_.pptx'
            collections['checks'].update(
                {'filename': {"$exists": 0}},
                {'$set': {'filename': '_.pptx'}},
                multi=True
            )
            collections['checks'].update(
                {'user': {"$exists": 0}},
                {'$set': {'user': 'moevm'}},
                multi=True
            )

            # calc score for all checks w/score=-1
            for check in collections['checks'].find({'score': -1}):
                score = Check(check).calc_score()
                collections['checks'].update(
                    {'_id': check['_id']},
                    {'$set': {'score': score}}
                )

            # update criteria.slides_number
            for user in collections['users'].find():
                new_criteria = {
                    12: [10, 12],
                    15: [13, 15]
                }[user['criteria']['slides_number']]
                collections['users'].update(
                    {'_id': user['_id']},
                    {'$set': {'criteria.slides_number': new_criteria}}
                )

            # causes unusual behavior - so, commented
            """
            # add 'verdict' to all criterias in checks fields
            criterias = tuple(Checks().get_checks().keys())
            for criteria in criterias:
                collections['checks'].update(
                    {f'{criteria}.verdict': {'$exists': 0}},
                    {'$set': {f'{criteria}.verdict': ''}},
                    multi=True
                )
            """
        else:
            raise Exception(f'Неподдерживаемый переход с версии {prev_version}')


class Version21(Version):
    VERSION_NAME = '2.1'
    CHANGES = '0/1 -> T/F; criteria.slides_number: [] -> {}'

    @classmethod
    def update_database(cls, collections, prev_version):
        if prev_version in (Version10.VERSION_NAME, Version11.VERSION_NAME, Version20.VERSION_NAME):

            # mv from 0/-1 -> T/F
            for check in collections['checks'].find({}):
                check_dt = Check(check).enabled_checks.items()
                upd_check = {k: False if v == -1 else v for k, v in check_dt}
                collections['checks'].update(
                    {'_id': check['_id']},
                    {'$set': upd_check}
                )

            for user in collections['users'].find():
                criteria_dt = Check(user['criteria']).enabled_checks
                upd_criteria = {k: False if v == -1 else True for k, v in criteria_dt.items()}
                upd_criteria['slides_number'] = {"sld_num": criteria_dt['slides_number'], "detect_additional": True} if \
                    upd_criteria['slides_number'] else False
                collections['users'].update(
                    {'_id': user['_id']},
                    {'$set': {'criteria': upd_criteria}}
                )

        else:
            raise Exception(f'Неподдерживаемый переход с версии {prev_version}')


class Version22(Version):
    VERSION_NAME = '2.2'
    CHANGES = 'Changes criteria field in user to dict with enabled values\n' \
              '(affects Checks init). Moves criteria fields in existing Checks\n' \
              'into a signle dict.'

    @classmethod
    def update_database(cls, collections, prev_version):
        if prev_version in (
                Version10.VERSION_NAME, Version11.VERSION_NAME, Version20.VERSION_NAME, Version21.VERSION_NAME):
            criteria_keys = ('slides_number', 'slides_enum', 'slides_headers', 'goals_slide',
                             'probe_slide', 'actual_slide', 'conclusion_slide', 'slide_every_task',
                             'conclusion_actual', 'conclusion_along')
            check_info = ('score', 'filename', 'conv_pdf_fs_id', 'user',
                          'is_passbacked', 'lms_passback_time')

            unset_fields_keys = [f'criteria.{k}' for k in check_info]
            unset_fields = dict.fromkeys(unset_fields_keys, 1)
            for user in collections['users'].find():
                criteria = user['criteria']
                reorder_criteria = {k: criteria.get(k, False) for k in criteria_keys}
                collections['users'].update_one(
                    {'_id': user['_id']},
                    {'$set': {'criteria': reorder_criteria}}
                )
            collections['users'].update_many({}, {"$unset": unset_fields})

            pipeline = [{'$project': {'enabled_checks': dict((f'{k}', f'${k}') for k in criteria_keys),
                                      **dict.fromkeys(check_info, 1)}},
                        {'$out': 'checks'}]
            collections['checks'].aggregate(pipeline=pipeline)
        else:
            raise Exception(f'Неподдерживаемый переход с версии {prev_version}')


class Version30(Version):
    VERSION_NAME = '3.0'
    CHANGES = 'Implementation of criterion packs and cancellation of criteria field in user as dict with enabled values'

    @staticmethod
    def map(key, value):
        if key == 'slides_number':
            result = {
                'id': key,
                'name': "Количество основных слайдов"
            }
        if key == 'slides_enum':
            result = {
                'id': key,
                'name': "Нумерация слайдов"
            }
        if key == 'slides_headers':
            result = {
                'id': key,
                'name': "Заголовки слайдов присутствуют и занимают не более двух строк"
            }
        if key == 'goals_slide':
            result = {
                'id': 'find_slides',
                'name': "Слайд 'Цель и задачи'"
            }
        if key == 'probe_slide':
            result = {
                'id': 'find_slides',
                'name': "Слайд 'Апробация работы'"
            }
        if key == 'actual_slide':
            result = {
                'id': 'find_on_slide',
                'name': "Слайд с описанием актуальности работы"
            }
        if key == 'conclusion_slide':
            result = {
                'id': 'find_slides',
                'name': "Слайд с заключением"
            }
        if key == 'slide_every_task':
            result = {
                'id': key,
                'name': "Наличие слайдов, посвященных задачам"
            }
        if key == 'conclusion_actual':
            result = {
                'id': key,
                'name': "Соответствие заключения задачам",
            }
        if key == 'conclusion_along':
            result = {
                'id': 'future_dev',
                'name': "Наличие направлений дальнейшего развития"
            }
        if key == 'template_name':
            result = {
                'id': key,
                'name': 'Соответствие названия файла шаблону'
            }
        result['score'] = float(value.get('pass', 0))
        result['verdict'] = value.get('verdict', '')
        return result

    @classmethod
    def update_database(cls, collections, prev_version):
        if prev_version in (Version22.VERSION_NAME,):
            base_pres_pack = 'BasePresentationCriterionPack'
            # set criteria for all user as base pres pack id
            collections['users'].update_many({}, {'$set': {'criteria': base_pres_pack, 'file_type': 'pres'}})
            # update criteria results
            for check in collections['checks'].find():
                new_list = [cls.map(k, v) for k, v in check['enabled_checks'].items() if v]
                collections['checks'].update_one({'_id': check['_id']}, {'$set': {'enabled_checks': new_list}})
        else:
            raise Exception(f'Неподдерживаемый переход с версии {prev_version}')


class Version31(Version):
    VERSION_NAME = '3.1'
    CHANGES = 'Изменена структура наборов критериев - file_type: "pres" => {"type": "pres"}. Обновлены наборы и пользователи'

    @classmethod
    def update_database(cls, collections, prev_version):
        if prev_version in (Version30.VERSION_NAME,):
            packs = {
                'pres': {'type': 'pres'},
                'report': {'type': 'report', 'report_type': 'LR'}
            }
            # set new file_type for pack depends on old type
            for pack_name in packs:
                collections['criteria_pack'].update_many({'file_type': pack_name},
                                                         {'$set': {'file_type': packs[pack_name]}})
                collections['users'].update_many({'file_type': pack_name}, {'$set': {'file_type': packs[pack_name]}})
                collections['checks'].update_many({'file_type': pack_name}, {'$set': {'file_type': packs[pack_name]}})
        else:
            raise Exception(f'Неподдерживаемый переход с версии {prev_version}')


VERSIONS = {
    '1.0': Version10,
    '1.1': Version11,
    '2.0': Version20,
    '2.1': Version21,
    '2.2': Version22,
    '3.0': Version30,
    '3.1': Version31,
}
LAST_VERSION = '3.1'

for _, ver in VERSIONS.items():
    print(ver.to_dict())
