import requests
import json
import time

import pygame

from helpers import get_horn 
from lights import goal_light, app_on_light, pregame_light, victory_light, end_of_period_light, turn_off_lights, fut_light
from config import BASE_API_URL, TODAY

class Game:

    def __init__(self, user_team, stream_delay, enable_audio, enable_lights, led_count):
        # Get configuration data
        self.team = user_team
        self.stream_delay = int(stream_delay)
        self.enable_audio = enable_audio
        self.enable_lights = enable_lights
        self.led_count = int(led_count)

        # set and initialize goal horn
        self.goal_horn = get_horn(self.team)
        pygame.mixer.init()
        pygame.mixer.music.load(self.goal_horn)

    
    def game_info(self):
        r = requests.get(f'{BASE_API_URL}score/{TODAY}')
        # r = requests.get(f'{BASE_API_URL}score/2024-10-08')
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

        # make initial API request to get the game data
        r = requests.get(f"{BASE_API_URL}gamecenter/{self.game_id}/play-by-play")
        data = json.dumps(r.json(), indent=4)
        # save file for testing
        with open('game.json', 'w') as f:
            f.write(data)
        data = json.loads(data) # load json for parsing    

        # for testing, get rid of this some day
        # with open("game.json", "r") as f:
        #     data = json.load(f)

        self.game_state = data["gameState"]
        self.period = data["displayPeriod"]

        self.home_score = data["homeTeam"]["score"]
        self.away_score = data["awayTeam"]["score"]

        self.stop_loop = False
        while True:
            self.watching = True
            if self.stop_loop:
                turn_off_lights(self.led_count)
                break

            # API request to update game data
            r = requests.get(f"{BASE_API_URL}gamecenter/{self.game_id}/play-by-play")
            data = json.dumps(r.json(), indent=4)
            # # save file for testing, delete this eventually
            with open('game.json', 'w') as f:
                f.write(data)
            data = json.loads(data) # load json for parsing

            # load json file for testing
            # with open("game.json", "r") as f:
            #     data = json.load(f)

            self.game_state = data["gameState"]

            # check non live game statuses... I really hope this is all of them
            # OFF status will break the loop and check if your team won. If so, it will do a victory dance
            if self.game_state != "LIVE":
                if self.game_state == "FUT":
                    print("The game has not started yet. Checking again in 30 minutes.", flush=True)
                    fut_light(self.led_count) if self.enable_lights else False
                    time.sleep(1800)
                    continue
                elif self.game_state == "PRE":
                    print("The game is about to start. Checking again in 2 minutes.", flush=True)
                    pregame_light(self.led_count) if self.enable_lights else False
                    time.sleep(120)
                    continue
                elif self.game_state == "OFF": 
                    print("The game is over.", flush=True)
                    
                    if self.home and self.home_score > self.away_score or self.away and self.away_score > self.home_score:
                        self.win = True
                    else:
                        self.win = False

                    if self.win:
                        victory_light(self.led_count) if self.enable_lights else False
                        print(f"{self.team} wins!!!", flush=True)
                    else:
                        # do sad stuff
                        print(f"{self.team} lost. :(", flush=True)
                    
                    turn_off_lights(self.led_count)
                    break

            # App starts running here. Only way to get to this point in the loop 
            # is if game state is LIVE. Unless there is a game state that idk about
            # I wonder what the game states are.... THERE IS NO DOCUMENTATION!
            app_on_light(self.led_count) if self.enable_lights else False
            
            # set new home score
            new_home_score = data["homeTeam"]["score"]
            new_away_score = data["awayTeam"]["score"]
            
            # Check scores, play horn, flash lights, go nuts!
            if new_home_score > self.home_score and self.home:
                pygame.mixer.music.play() if self.enable_audio else False
                goal_light(self.led_count) if self.enable_lights else False
                print(f"{self.team} scores!!", flush=True)

            if new_away_score > self.away_score and self.away:
                pygame.mixer.music.play() if self.enable_audio else False
                goal_light(self.led_count)  if self.enable_lights else False
                print(f"{self.team} scores!!", flush=True)
            
            # reset scores for next check
            self.home_score = new_home_score
            self.away_score = new_away_score

            # get period from fresh data
            new_period = data["displayPeriod"]

            # if period changes, do a light show!
            if new_period > self.period:
                end_of_period_light(self.led_count) if self.enable_lights else False
                pass
            
            # reset period for next check
            self.period = new_period

            print(f"Home score is: {self.home_score}\nAway score is: {self.away_score}", flush=True)

            time.sleep(self.stream_delay)

        self.watching = False
        turn_off_lights(self.led_count)