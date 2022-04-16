import os
import pytz
from datetime import datetime


timezone_offset = pytz.timezone(os.environ.get('TZ', 'Europe/Moscow')).utcoffset(datetime.now())
