# time_utils.py
# gives ISO time

from datetime import datetime, timezone

def iso_now():
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"