import json
import re
import os
import requests
from datetime import datetime
from dateutil import tz
import pytz
import pygame
from bs4 import BeautifulSoup


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


def update_colors_json():

    r = requests.get('https://teamcolorcodes.com/nhl-team-color-codes/')
    soup = BeautifulSoup(r.text, 'html.parser')

    team_links = soup.find_all("a", class_="team-button")

    json_output = {}

    i=0
    for a in team_links:
        url = a['href']

        # Regular expression to match everything between "https://teamcolorcodes.com/" 
        # and either "-color-codes/" or "-team-colors/"
        url_pattern = r'https://teamcolorcodes\.com/(.*?)-(color-codes|team-colors|colors)/'
        url_str = re.search(url_pattern, url)
        url_str = url_str.group(1)
        team_name = url_str.replace('-', ' ').title()
        
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        
        # Define the regular expression pattern to find "RGB: ("
        rgb_pattern = re.compile(r'RGB:?\s*\(')
        rgb_strs = soup.find_all(string=rgb_pattern)

        rgb_values = {}
        
        i=0
        for match in rgb_strs:
            
            # Regular expression to match the RGB values inside parentheses
            rgb_value_pattern = r'RGB:?\s*\((\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})\)'
            # Search for the pattern in the text
            rgb_value_str = re.search(rgb_value_pattern, match)
            
            if rgb_value_str:
                r, g, b = rgb_value_str.groups()
                rgb = (int(r), int(g), int(b))
                i+=1
                
                rgb_values[i] = rgb
        
        json_output[team_name] = rgb_values
        

    with open('colors/colors.json', 'w') as f:
        f.write(json.dumps(json_output, indent=2))