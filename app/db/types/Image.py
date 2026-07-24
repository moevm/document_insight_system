from app.db.types.PackableWithId import PackableWithId


class Image(PackableWithId):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        dictionary = dictionary or {}
        self.check_id = dictionary.get('check_id')
        self.caption = dictionary.get('caption', '')
        self.image_data = dictionary.get('image_data')
        self.image_size = dictionary.get('image_size')
        self.text = dictionary.get('text')
        self.page = dictionary.get('page')

    def pack(self):
        package = super().pack()
        package['check_id'] = str(self.check_id)
        return package
