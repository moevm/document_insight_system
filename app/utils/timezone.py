import os
from datetime import datetime

import pytz

timezone_offset = pytz.timezone(os.environ.get('TZ', 'Europe/Moscow')).utcoffset(datetime.now())
