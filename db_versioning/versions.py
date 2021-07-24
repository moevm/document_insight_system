from app.bd_helper.bd_types import Checks


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
        """
        raise NotImplementedError()
    
    @classmethod
    def to_dict(cls):
        return dict(
            version = cls.VERSION_NAME,
            changes = cls.CHANGES
        )

    @staticmethod
    def get_version(version_name):
        for version in VERSIONS:
            if version.version == version_name:
                return version
        return None 


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
    CHANGES = "Изменен подход в версионированию БД: исправляются минусы предыдущих версий " \
              "(поля filename/user/score заполняются верными значениямм).\n" \
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
                user_doc = collections['users'].find_one({'presentations': presentation['_id'] })
                user = user_doc.get('username', 'moevm') if user_doc else 'moevm'
                for check_id in presentation["checks"]:
                    collections['checks'].update(
                        {"_id": check_id},
                        { '$set': { 'filename': filename, 'user': user } }
                    )
            
            # if we have checks without presentation == after prev loop it doesn't include filename/user field
            # set default user='moevm', filename='_.pptx'
            collections['checks'].update(
                {'filename': { "$exists": 0}},
                {'$set': {'filename': '_.pptx'}},
                multi=True
            )
            collections['checks'].update(
                {'user': { "$exists": 0}},
                {'$set': {'user': 'moevm'}},
                multi=True
            )

            # calc score for all checks w/score=-1
            for check in collections['checks'].find({'score': -1}):
                score = Checks(check).calc_score()
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

            # add 'verdict' to all criterias in checks fields
            criterias = tuple(Checks().get_checks().keys())
            for criteria in criterias:
                collections['checks'].update(
                    {f'{criteria}.verdict': {'$exists': 0}},
                    {'$set': {f'{criteria}.verdict': ''}},
                    multi=True
                )
        else:
            raise Exception(f'Неподдерживаемый переход с версии {prev_version}')


VERSIONS = {
    '1.0': Version10,
    '1.1': Version11,
    '2.0': Version20,
}
LAST_VERSION = '2.0'


for _, ver in VERSIONS.items():
    print(ver.to_dict())