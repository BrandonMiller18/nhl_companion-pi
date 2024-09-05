import json

from datetime import datetime
from dateutil import tz
import pytz

from game import Game

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


if __name__ == '__main__':
    game = Game()
    game.game_info()

    game_info = {
        'User team abbr': game.team,
        'Game date': game.date,
        'Game start time': standard_date(game.game_start_time),
        'Game state': game.game_state,
        'User team plays': game.is_game,
        'User team is home': game.home,
        'User team is away': game.away,
        'Game ID': game.game_id,
        'Home team name': game.home_team,
        'Home team logo': game.home_team_logo,
        'Away team name': game.away_team,
        'Away team logo': game.away_team_logo
    }
    print(f"\n{json.dumps(game_info, indent=4)}")
