from flask import render_template, request
from webapp.app import app
import data.nfl as nfl


@app.route("/")
def drive_chart():
    """
        Renders drive chart along with UI to select which year / week / game / drive
    """
    return render_template("drive_chart.html")


@app.route('/get_json_data/')
def get_json_data():
    # get number of items from the javascript request
    week = request.args.get('week', 1, type=int)
    year = request.args.get('year', '2013', type=str)
    game = request.args.get('game', 1, type=int)
    drive = request.args.get('drive', 1, type=int)
    data = nfl.drive_to_json(year, week, game, drive)
    return data


@app.route('/get_drives_data')
def get_drive_data():
    """
        ajax call from the game selection form
        returns json of drive summary for each drive in game
    """
    week = request.args.get('week', 1, type=int)
    year = request.args.get('year', '2013', type=str)
    game = request.args.get('game', 1, type=int)
    return nfl.get_game_drive_json(year, week, game)
