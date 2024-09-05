import json
import time
import requests
from config import BASE_API_URL, TODAY

class Game:

    def __init__(self):
        self.team = str(input('Input team abbr: ').upper())
        self.stream_delay = int(input("Set strean delay: "))

    
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
                    self.game_start_time = None
                    self.home = False
                    self.away = False
                    self.home_team = None
                    self.home_team_logo = None
                    self.away_team = None
                    self.away_team_logo = None
                    self.game_id = None


    def watch_game(self):
        print("Watch game")
        game_states = {
            "Not started": "FUT",
            "Pregame": "PRE",
            "Live": "LIVE",
            "Game over": "OFF"
        }

        # r = requests.get(f"{BASE_API_URL}gamecenter/{self.game_id}/play-by-play")
        # data = json.dumps(r.json(), indent=4)
        # data = json.loads(data) # load json for parsing

        with open("game.json", "r") as f:
                data = json.load(f)

        game_state = data["gameState"]
        period = data["displayPeriod"]

        home_score = data["homeTeam"]["score"]
        away_score = data["awayTeam"]["score"]

        while True:
            # r = requests.get(f"{BASE_API_URL}gamecenter/{self.game_id}/play-by-play")
            # data = json.dumps(r.json(), indent=4)
            # data = json.loads(data) # load json for parsing

            # for testing
            with open("game.json", "r") as f:
                data = json.load(f)

            game_state = data["gameState"]
            if game_state != "LIVE":
                if game_state == "FUT":
                    print("The game has not started yet. Checking again in 30 minutes.")
                    time.sleep(1800)
                    continue
                elif game_state == "PRE":
                    print("The game is about to start. Checking again in 2 minutes.")
                    time.sleep(120)
                    continue
                elif game_state == "OFF": 
                    print("The game is over.")
                    
                    if self.home and home_score > away_score or self.away and away_score > home_score:
                        self.win = True
                    else:
                        self.win = False

                    if self.win:
                        # do victory celebration
                        print(f"{self.team} wins!!!")
                    else:
                        # do sad stuff
                        print(f"{self.team} lost. :(")
                    
                    break


            period = data["displayPeriod"]

            new_home_score = data["homeTeam"]["score"]
            new_away_score = data["awayTeam"]["score"]

            if new_home_score > home_score and self.home:
                # play horn, flash lights
                print(f"{self.team} scores!!", flush=True)

            if new_away_score > away_score and self.away:
                # play horn, flash lights
                print(f"{self.team} scores!!", flush=True)

            home_score = new_home_score
            away_score = new_away_score

            print(f"Home score is: {home_score}\nAway score is: {away_score}")

            time.sleep(self.stream_delay)
