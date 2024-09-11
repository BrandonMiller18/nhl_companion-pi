from flask import Flask, render_template

# from helpers import standard_date
# from game import Game

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/start')
def configure_game():

    return render_template("start.html")


# game = Game()
# game.game_info()
# 
# game_info = {
#     'User team abbr': game.team,
#     'Game date': game.date,
#     'Game start time': standard_date(game.game_start_time) if game.game_start_time else None,
#     'Game state': game.game_state,
#     'User team plays': game.is_game,
#     'User team is home': game.home,
#     'User team is away': game.away,
#     'Game ID': game.game_id,
#     'Home team name': game.home_team,
#     'Home team logo': game.home_team_logo,
#     'Away team name': game.away_team,
#     'Away team logo': game.away_team_logo
# }
# 