from datetime import datetime
from dateutil import tz
import pytz


def standard_date(dt):
    """Takes a naive datetime stamp, tests if time ago is > than 1 year,
       determines user's local timezone, outputs stamp formatted and at local time."""

    # datetime format
    fmt = "%Y-%m-%dT%H:%M:%SZ"  
    # convert dt str to datetime object
    dt = datetime.strptime(dt, fmt)

    # get users local timezone from the dateutils library
    # http://stackoverflow.com/a/4771733/523051
    users_tz = tz.tzlocal()

    # give the naive stamp timezone info
    utc_dt = dt.replace(tzinfo=pytz.utc)
    # convert from utc to local time
    loc_dt = utc_dt.astimezone(users_tz)
    # apply formatting
    f = loc_dt.strftime(fmt)

    # convert to just time, strip date
    return f[len(f) - 9:-1]