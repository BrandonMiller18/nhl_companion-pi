import json
import os.path
from flask import Flask, render_template, redirect, request, flash, url_for

from helpers import standard_date, update_teams
from game import Game

app = Flask(__name__)

app.config.from_pyfile('config.py')

# update team abbreviations list. Happens sever side when the app is started. To refresh, restart the flask app
team_abbreviations = update_teams()

@app.route('/')
def index():

    if os.path.isfile('config.json'):
        with open('config.json', 'r') as f:
            data = json.load(f)

        return render_template('index.html', data=data, team_abbreviations=team_abbreviations)

    return render_template("index.html", team_abbreviations=team_abbreviations)

@app.route('/update', methods=['POST'])
def configure_game():

    user_team = request.form.get('user_team')
    stream_delay = request.form.get('stream_delay')

    with open('config.json', 'w') as f:
        data = {
            "user_team": user_team,
            "stream_delay": 0 if stream_delay == '' else stream_delay
        }

        f.write(json.dumps(data))

        flash("Configuration has been updated!", "success")

    return redirect(url_for('index'))


@app.route('/start', methods=['GET', 'POST'])
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

    # instatiate game object and start the game
    global game 
    game = Game(user_team=user_team, stream_delay=stream_delay)
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
        flash("App was stopped by user.", "danger")
        return redirect(url_for('index'))

    return render_template('start_game.html', data=game_info)

@app.route('/_end-game')
def end_game():
    game.stop_loop = True
    res = f"stop_loop set to: {game.stop_loop}"
    print(res)
    return res