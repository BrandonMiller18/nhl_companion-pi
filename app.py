import json
import os.path
from flask import Flask, render_template, redirect, request, flash, url_for

from helpers import standard_date
from game import Game

app = Flask(__name__)

app.config.from_pyfile('config.py')

@app.route('/')
def index():

    if os.path.isfile('config.json'):
        with open('config.json', 'r') as f:
            data = json.load(f)

        return render_template('index.html', data=data)

    return render_template("index.html")

@app.route('/update', methods=['POST'])
def configure_game():

    user_team = request.form.get('user_team')
    stream_delay = request.form.get('stream_delay')

    with open('config.json', 'w') as f:
        data = {
            "user_team": user_team,
            "stream_delay": stream_delay
        }

        f.write(json.dumps(data))

        flash("Configuration has been updated!")

    return redirect(url_for('index'))


@app.route('/watch', methods=['GET'])
def watch_game():

    if not os.path.isfile('config.json'):
        flash("Missing config.json file. Must set configuration first!", 'error')
        return redirect(url_for('index'))

    with open('config.json', 'r') as f:
        data = json.load(f)
        user_team = data['user_team']
        stream_delay = data['stream_delay']

    game = Game(user_team=user_team, stream_delay=stream_delay)
    game.game_info()
    game_info = {
        'User team abbr': game.team,
        'Game date': game.date,
        'Game start time': standard_date(game.game_start_time) if game.game_start_time else None,
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

    print(game_info, flush=True)

    return render_template('watch.html', data=game_info) 