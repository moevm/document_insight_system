from bson import ObjectId

from app.db.types.Packable import Packable


class PackableWithId(Packable):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        dictionary = dictionary or {}
        if '_id' in dictionary:
            self._id = ObjectId(dictionary.get('_id'))

    def pack(self, to_str=False):
        package = super().pack()
        if '_id' in package:
            package['_id'] = self._id if not to_str else str(self._id)
        return package
