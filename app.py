import json
import time
import os.path
from threading import Thread
from flask import Flask, render_template, redirect, request, flash, url_for

from helpers import standard_date, update_teams
from lights import no_game_light
from game import Game

app = Flask(__name__)

app.config.from_pyfile('config.py')

# update team abbreviations list. Happens sever side when the app is started. To refresh, restart the flask app
team_abbreviations = update_teams()

@app.route('/')
@app.route('/<arg>')
def index(arg=0):
    if arg == '1':
        flash("User has stopped the app.", "danger")
        return redirect(url_for('index'))
    
    if arg == '2':
        flash("There is no game running currently!", "danger")
        return redirect(url_for('index'))
    
    if arg == '3':
        flash("Game has started! Enjoy!", "success")
        return redirect(url_for('index'))
    

    # HACK
    # see if there is a game happening. there might not be, thus try/except...
    # if an error happens here, there is not a game object... so set watching to false.
    # The "watching" variable determines page content
    try:
        if game.watching:
            watching = True
        else:
            watching = False
    except:
        watching = False

    # check for configuration file
    if os.path.isfile('config.json'):
        with open('config.json', 'r') as f:
            data = json.load(f)
    else:
        data = None

    return render_template('index.html', data=data, team_abbreviations=team_abbreviations, watching=watching)


@app.route('/update', methods=['POST'])
def configure_game():
    # handle form submission from homepage, returns redirect to homepage 

    # get data fields
    user_team = request.form.get('user_team')
    stream_delay = request.form.get('stream_delay')
    enable_lights = request.form.get('lights')
    enable_audio = request.form.get('audio')
    led_count = request.form.get('led_count')

    if os.path.isfile('config.json'):
        with open('config.json', 'r') as f:
            data = json.load(f)
            current_led_count = data['led_count']
    else:
        data = None
        current_led_count = '0'

    # create config.json file and write form data to file for later use
    with open('config.json', 'w') as f:
        data = {
            "user_team": user_team,
            "stream_delay": data['stream_delay'] if stream_delay == '' else stream_delay,
            "enable_lights": True if enable_lights else False,
            "enable_audio": True if enable_audio else False,
            "led_count": led_count if led_count else current_led_count,
        }

        f.write(json.dumps(data))

    # show user confirmation message
    flash("Configuration has been updated!", "success")

    return redirect(url_for('index'))


@app.route('/start')
def start_game_lp():
    # landing page for START APP buttons. This is to prevent,
    # as best as possible, endless loading in the user interface.
    # however, this is not a public website, so who cares.

    # HACK
    # see if there is a game happening. there might not be, thus try/except...
    # if an error happens here, there is not a game object... so set watching to false
    # The "watching" variable determines page content
    try:
        if game.watching:
            watching = True
        else:
            watching = False
    except:
        watching = False

    return render_template('start.html', watching=watching)


@app.route('/watch-game', methods=['GET', 'POST'])
def start_game():

    # Check if the config.json file exists
    if not os.path.isfile('config.json'):
        flash("Missing config.json file. Must set configuration first!", 'danger')
        return redirect(url_for('index'))

    # get team and stream delay values from config file
    with open('config.json', 'r') as f:
        data = json.load(f)
        user_team = data['user_team']
        stream_delay = data['stream_delay']
        enable_lights = data['enable_lights']
        enable_audio = data['enable_audio']
        led_count = data['led_count']

    # instatiate game object and start the game.. Pass config vars to Game class
    global game 
    game = Game(user_team=user_team,
                stream_delay=stream_delay,
                enable_audio=enable_audio,
                enable_lights=enable_lights,
                led_count=led_count
            )
    
    # Get game info for user team
    game.game_info()

    # if user team does not play, show error and return to homepage
    if not game.is_game:
        no_game_light(int(led_count)) if enable_lights else False
        flash(f"{game.team} does not play today.", "danger")
        return redirect(url_for('index'))
    else:
        # if you got this far, there is a game. Watch it.
        # run game on a different thread so the user does not get hung
        # NOTE: I have no idea how this actually works..
        Thread(target=game.watch_game).start()
        
    # wait for game.watching attribute to be defined before continuing
    while not hasattr(game, 'watching'):
        pass
    
    return redirect(url_for('index', arg=3))


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/_end-game')
def end_game():
    # request here means user clicked on cancel app butto
    try:
        game
    except NameError:
        # send user back home with stop_loop path set to 2
        return redirect(url_for('index', arg=2))
        
    # set stop_loop to true. Next time the app updates, the While True loop will break and game will end
    # BUG - when in preview mode, it can take up to 30 min to do this, which sucks.
    # TRY TO FIND A WAY TO MAKE THIS HAPPEN IMMEDIATELY
    game.stop_loop = True
    
    # print out message to make sure its still working
    i = 0
    while game.watching:
        print(f"Cancelling game... {i}", flush=True)
        time.sleep(1)
        i+=1

    # send user back home with arg path set to 1
    return redirect(url_for('index', arg=1))


@app.route('/api/colors')
def colors_api():
    with open('colors/colors.json') as f:
        data = json.load(f)
    
    return json.dumps(data, indent=4)