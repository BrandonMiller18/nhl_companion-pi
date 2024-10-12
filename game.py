import requests
import json
import time
from datetime import date

import pygame

from helpers import get_horn 
from lights import goal_light, app_on_light, pregame_light, victory_light, period_light, turn_off_lights, fut_light, init_game_light
from config import BASE_API_URL

class Game:

    def __init__(self, user_team, stream_delay, enable_audio, enable_lights, led_count):
        # Get configuration data
        self.team = user_team
        self.stream_delay = int(stream_delay)
        self.enable_audio = enable_audio
        self.enable_lights = enable_lights
        self.led_count = int(led_count)
        
        # get team name - use NHL records API for list of franchises
        r = requests.get("https://records.nhl.com/site/api/franchise")
        data = json.dumps(r.json(), indent=4)
        data = json.loads(data) # load json for parsing
        
        for team in data['data']:
            if team['teamAbbrev'] == self.team:
                self.team_full_name = team['fullName'].replace('.', '')

        # set team color
        with open('colors/colors.json', 'r') as f:
            data = json.load(f)
            primary_color = data[self.team_full_name]['1']
            self.primary_color = (primary_color[0], primary_color[1], primary_color[2])
            
            secondary_color = data[self.team_full_name]['2']
            self.secondary_color = (secondary_color[0], secondary_color[1], secondary_color[2])

        # set and initialize goal horn
        self.audio_error = False
        if self.enable_audio:
            try:
                self.goal_horn = get_horn(self.team)
                pygame.mixer.init()
                pygame.mixer.music.load(self.goal_horn)
            except pygame.error as message:
                print("--\nCould not load pygame audio, probably because there is no audio device.")
                print(f"{message}\n--")
                self.audio_error = True
    
    
    def game_info(self):
        # Get and set all the information about the selected team's game

        r = requests.get(f'{BASE_API_URL}score/{date.today()}')
        data = json.dumps(r.json(), indent=4)

        # save file for testing
        with open('todays_games.json', 'w') as f:
            f.write(data)

        data = json.loads(data) # load json for parsing
        self.date = data["currentDate"]

        # If the 'games' array has len=0, then there are no games today and the rest of this is pointless
        if len(data['games']) == 0:
            self.is_game = False
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
                    # Look for game which includes the selected team
                    self.is_game = True
                    self.game_state = game["gameState"]
                    self.game_start_time = game["startTimeUTC"]
                    self.game_id = game['id']
                    self.away_team = game['awayTeam']['name']['default']
                    self.away_team_logo = game['awayTeam']['logo']
                    self.home_team = game['homeTeam']['name']['default']
                    self.home_team_logo = game['homeTeam']['logo']

                    # Set home and away values
                    if game['awayTeam']['abbrev'] == self.team:
                        self.home = False
                        self.away = True

                    if game['homeTeam']['abbrev'] == self.team:
                        self.home = True
                        self.away = False

                    # Pointless check for home and away both being set to true
                    if self.home == self.away:
                        raise Exception(f"HOME and AWAY values cannot be equal.\nHome = {self.home}\nAway = {self.away}")
                    
                    # Break the for loop becuase the values have been set
                    break
                
                # If team was not found above, that means there are NHL games today, but the user team does not play
                else:
                    self.is_game = False
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
        init_game_light(self.led_count) if self.enable_lights else False

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

        # set initial values before while loop
        self.game_state = data["gameState"]
        self.period = data["displayPeriod"]
        self.inIntermission = data["clock"]["inIntermission"] if self.game_state == "LIVE" else False
        self.home_score = data["homeTeam"]["score"]
        self.away_score = data["awayTeam"]["score"]

        self.stop_loop = False
        len_plays = 0
        i = 0
        app_on_light(self.led_count, self.primary_color) if self.enable_lights else False
        while True:
            self.watching = True # used to block user interface from starting multiple games
            if self.stop_loop:
                turn_off_lights(self.led_count)
                break

            # API request to update game data
            r = requests.get(f"{BASE_API_URL}gamecenter/{self.game_id}/play-by-play")
            data = json.dumps(r.json(), indent=4)
            # save file for testing, delete this eventually
            with open('game.json', 'w') as f:
                f.write(data)
            data = json.loads(data) # load json for parsing
            
            # check non live game statuses... I really hope this is all of them
            # OFF/FINAL status will break the loop and check if your team won. If so, it will do a victory dance
            self.game_state = data["gameState"]
            if self.game_state != "LIVE":
                if self.game_state == "FUT":
                    print("The game has not started yet. Checking again in 5 minutes.", flush=True)
                    fut_light(self.led_count) if self.enable_lights else False
                    time.sleep(300) #300
                    continue
                elif self.game_state == "PRE":
                    print("The game is about to start. Checking again in 2 minutes.", flush=True)
                    pregame_light(self.led_count) if self.enable_lights else False
                    time.sleep(120) #120
                    continue
                elif self.game_state in ("OFF", "FINAL"): 
                    print("The game is over.", flush=True)
                    
                    if (self.home and self.home_score > self.away_score) or (self.away and self.away_score > self.home_score):
                        self.win = True
                    else:
                        self.win = False

                    if self.win:
                        victory_light(self.led_count, self.primary_color, self.secondary_color) if self.enable_lights else False
                        print(f"{self.team} wins!!!", flush=True)
                    else:
                        # do sad stuff
                        print(f"{self.team} lost. :(", flush=True)
                    
                    turn_off_lights(self.led_count)
                    break
            
            # App starts running here. Only way to get to this point in the loop 
            # is if game state is LIVE. Unless there is a game state that idk about
            # I wonder what the game states are.... THERE IS NO DOCUMENTATION!
            
            # find the number of new plays to check...
            # if the newly fetched array is longer than the known len, set the len and check the plays
            plays = data['plays']
            if len_plays == 0:
                len_plays = len(plays)
                print(f'Length of plays array: {len_plays}\nLoop iteration: {i}')
                i+=1
                continue
            
            if len(plays) > len_plays:
                len_new_plays = len(plays) - len_plays
                len_plays = len(plays)
            else:
                print(f'Length of plays array: {len_plays}\nLoop iteration: {i}')
                i+=1
                continue
            
            print(f'\nLength of plays array: {len_plays}')
            print(f'New plays: {len_new_plays}')
                       
            # check new plays since last refresh for fun stuff like goals
            plays_checked = 0
            for new_play in plays[-len_new_plays:]:
                print(new_play['typeDescKey'])
                if new_play['typeDescKey'] == 'goal':
                    if new_play['details']['homeScore'] > self.home_score and self.home:
                        time.sleep(self.stream_delay) # wait for stream
                        pygame.mixer.music.play() if self.enable_audio else False
                        goal_light(self.led_count) if self.enable_lights else False
                        print(f"{self.team} scores!!", flush=True)
                        
                        self.home_score = new_play['details']['homeScore']
                        
                    if new_play['details']['awayScore'] > self.away_score and self.away:
                        time.sleep(self.stream_delay) # wait for stream
                        pygame.mixer.music.play() if self.enable_audio else False
                        goal_light(self.led_count)  if self.enable_lights else False
                        print(f"{self.team} scores!!", flush=True)
                        
                        self.away_score = new_play['details']['awayScore']
                        
                    # ensure both scores are set
                    self.home_score = new_play['details']['homeScore']
                    self.away_score = new_play['details']['awayScore']
                        
                if new_play['typeDescKey'] == 'period-end' and not self.inIntermission:
                    time.sleep(self.stream_delay) # wait for stream
                    period_light(self.led_count) if self.enable_lights else False
                    self.inIntermission = True
                    
                if new_play['typeDescKey'] == 'period-start' and self.inIntermission:
                    time.sleep(self.stream_delay) # wait for stream
                    period_light(self.led_count) if self.enable_lights else False
                    self.inIntermission = False
                    
                plays_checked += 1
            
            print(f'Checked {plays_checked} plays.')


            print(f"Home score is: {self.home_score}\nAway score is: {self.away_score}\n")

            i+=1
            time.sleep(1) # wait one second before next refresh

        # if you got here the While True loop was broken, so you are not 
        # watching the game anymore. Turn it all off
        self.watching = False
        turn_off_lights(self.led_count)