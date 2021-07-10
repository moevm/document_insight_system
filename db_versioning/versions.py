class Version:
    def __init__(self, version='1.0', changes=None, info='First DB version'):
        self.version = version
        self.changes = changes
        self.info = info

    def to_dict(self):
        return vars(self)

def get_version(versio_name):
    for version in versions:
        if version.version == versio_name:
            return version
    return None 

version_1_0 = Version()    # начальная версия БД (до https://github.com/moevm/mse_auto_checking_slides_vaganov/pull/110)
version_1_1 = Version(
    version='1.1',
    changes={
        '1.0': {
            'checks': {
                '$set': {
                    'filename': '_.pptx',
                    'user': 'moevm'
                }
            }
        }
    },
    info="В коллекцию checks добавлены поля filename и user. Для перехода с версии 1.0 необходимо заполнить поля"
)

versions = (version_1_0, version_1_1)

for ver in versions:
    print(ver.to_dict())