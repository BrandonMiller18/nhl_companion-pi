import requests
import json
from config import BASE_API_URL, TODAY

class Game:

    def __init__(self, user_team):
        self.team = user_team

    
    def game_info(self):
        r = requests.get(f'{BASE_API_URL}score/{TODAY}')
        data = json.dumps(r.json(), indent=4)

        # save file for testing
        with open('todays_games.json', 'w') as f:
            f.write(data)

        data = json.loads(data) # load json for parsing
        self.date = data["currentDate"]

        if len(data['games']) == 0:
            self.is_game = False # no games today
            self.game_state = None
            self.game_start_time = None
            self.home = False
            self.away = False
            self.home_team = None
            self.home_team_logo = None
            self.away_team = None
            self.away_team_logo = None
            self.game_id = None
        else:
            for game in data['games']:
                if game['awayTeam']['abbrev'] == self.team or game['homeTeam']['abbrev'] == self.team:
                    self.is_game = True
                    self.game_state = game["gameState"]
                    self.game_start_time = game["startTimeUTC"]
                    self.game_id = game['id']
                    self.away_team = game['awayTeam']['name']['default']
                    self.away_team_logo = game['awayTeam']['logo']
                    self.home_team = game['homeTeam']['name']['default']
                    self.home_team_logo = game['homeTeam']['logo']

                    if game['awayTeam']['abbrev'] == self.team:
                        self.home = False
                        self.away = True

                    if game['homeTeam']['abbrev'] == self.team:
                        self.home = True
                        self.away = False

                    if self.home == self.away:
                        raise Exception(f"HOME and AWAY values cannot be equal.\nHome = {self.home}\nAway = {self.away}")
                    
                    break
                
                else:
                    self.is_game = False # selected team does not play
                    self.game_state = None
                    self.home = False
                    self.away = False
                    self.home_team = None
                    self.away_team = None
                    self.game_id = None

    
    def team_info(self):
        '''Function to get home and away team info such as arena, city, etc...'''
        pass