import json
import time
import os.path
from flask import Flask, render_template, redirect, request, flash, url_for

from helpers import standard_date, update_teams
from game import Game

app = Flask(__name__)

app.config.from_pyfile('config.py')

# update team abbreviations list. Happens sever side when the app is started. To refresh, restart the flask app
team_abbreviations = update_teams()

@app.route('/')
@app.route('/<stop_loop>')
def index(stop_loop=0):

    # check to see if there is a current game in progress, if there is we will adjust what is displayed on the homepage
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

    if stop_loop == '1':
        flash("User has stopped the app.", "danger")
        return redirect(url_for('index'))

    return render_template('index.html', data=data, team_abbreviations=team_abbreviations, watching=watching)


@app.route('/update', methods=['POST'])
def configure_game():

    user_team = request.form.get('user_team')
    stream_delay = request.form.get('stream_delay')
    enable_lights = request.form.get('lights')
    enable_audio = request.form.get('audio')

    with open('config.json', 'w') as f:
        data = {
            "user_team": user_team,
            "stream_delay": "5" if stream_delay == '' else stream_delay,
            "enable_lights": True if enable_lights else False,
            "enable_audio": True if enable_audio else False
        }

        f.write(json.dumps(data))

        flash("Configuration has been updated!", "success")

    return redirect(url_for('index'))


@app.route('/start')
def start_game_lp():

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

    # instatiate game object and start the game
    global game 
    game = Game(user_team=user_team, stream_delay=stream_delay, enable_audio=enable_audio, enable_lights=enable_lights)
    game.game_info()

    if not game.is_game:
        flash(f"{game.team} does not play today.", "danger")
        return redirect(url_for('index'))

    game.watch_game()

    game_info = {
        'user_team': game.team,
        'game_date': game.date,
        'game_start_time': standard_date(game.game_start_time) if game.game_start_time else None,
        'game_state': game.game_state,
        'is_game': game.is_game,
        'is_home': game.home,
        'is_away': game.away,
        'game_id': game.game_id,
        'home_team': game.home_team,
        'home_team_logo': game.home_team_logo,
        'away_team': game.away_team,
        'away_team_logo': game.away_team_logo,
        'home_score': game.home_score,
        'away_score': game.away_score
    }

    if game.stop_loop:
        return redirect(url_for('end-game'))

    return render_template('watch_game.html', data=game_info)


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/_end-game')
def end_game():
    game.stop_loop = True
    
    while game.watching:
        print("Cancelling game...", flush=True)
        time.sleep(1)

    return redirect(url_for('index', stop_loop=1))