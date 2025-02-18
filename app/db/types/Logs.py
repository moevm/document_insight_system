from app.db.types.Packable import Packable


class Logs(Packable):
    def __init__(self, dictionary=None):
        super().__init__(dictionary)
        dictionary = dictionary or {}
        self.timestamp = dictionary.get('timestamp', None)
        self.serviceName = dictionary.get('serviceName', None)
        self.levelname = dictionary.get('levelname', None)
        self.levelno = dictionary.get('levelno', None)
        self.message = dictionary.get('message', None)
        self.pathname = dictionary.get('pathname', None)
        self.filename = dictionary.get('filename', None)
        self.funcName = dictionary.get('funcName', None)
        self.lineno = dictionary.get('lineno', None)
