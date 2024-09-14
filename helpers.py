import json
import os
import requests
from datetime import datetime
from dateutil import tz
import pytz
import pygame


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


def update_teams():

    teams = []

    r = requests.get('https://api-web.nhle.com/v1/standings/now')
    # data = json.dumps(r.json())
    data = json.loads(json.dumps(r.json()))

    for team in data['standings']:
        teams.append(team['teamAbbrev']['default'])

    return teams

def get_horn(abbr):
    file = f"{os.getcwd()}/static/media/sounds/{abbr.lower()}.mp3"

    if not os.path.isfile(file):
        file = f"{os.getcwd()}/static/media/sounds/goal.mp3"


    return file