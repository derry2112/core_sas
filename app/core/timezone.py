import os
from datetime import datetime

import pytz
from dotenv import load_dotenv

load_dotenv()

GLOBAL_TIMEZONE = os.getenv("TIMEZONE", "UTC")


def make_aware(dt):
    if dt.tzinfo is not None:
        return dt
    else:
        tz = pytz.timezone(GLOBAL_TIMEZONE)
        return tz.localize(dt)


def get_timezone():
    tz = pytz.timezone(GLOBAL_TIMEZONE)
    print(f"Timezone loaded: {GLOBAL_TIMEZONE}")
    return datetime.now(tz)
