import nflgame
import json


def get_games(year, week):
    """
        Returns all the games for a given week
    """
    year = int(year)
    try:
        games = nflgame.games(year, week=week)
    except Exception as e:
        print e
        games = []
    return games


def get_game_drives(game):
    """
        Returns a list of drive objects from a NFL game
    """
    return [drive for drive in game.drives]


def get_drive_plays(drive):
    """
        Returns a list of plays from a drive
    """
    return [clean_play_data(play) for play in drive.plays]


def clean_play_data(play, config={}):
    """
        Removes expensive json that is not being used.
        Also flattens nflgame objects into json serializable format

        input:
                nflgame.play
        returns:
                dictionary representation of play
    """
    # removing unwanted play data for json
    if not config:
        config = {
            'time': '',
            'players': '',
            'drive': ''
        }

    if play.time:
        play.time = play.time.__dict__

    else:
        play.time = {}

    if play.yardline:
        play.yardline = play.yardline.__dict__
    else:
        play.yardline = {'offset': 50}
    play._Play__players = ''
    play.type = get_play_type(play)
    play.yards_gained = get_yards_gained(play)  # dependent on play_type

    # trim these out of configed
    if 'players' in config:
        play.players = ''
    else:
        play.players = play.players.__dict__
    if 'drive' in config:
        play.drive = ''
    else:
        play.drive = play.drive__dict__
    return play.__dict__


def get_play_type(play):
    """
        Parses the play to determine the play type.
        Current solution is more-or-less brute force
        input: 
            nflgame.play
        Returns:
            type of play [pass, rush, kick, fumble, penalty, sack, fg, touchdown, interception]
    """
    play_type = None
    play_info = play.__dict__
    type_legend = {
        "rushing_att": "rush",
        "passing_att": "pass",
        "kicking_tot": "kick",
        "punting_tot": "punt",
        "kicking_fga": "field_goal"
    }
    for option in type_legend:
        if option in play_info:
            play_type = type_legend[option]

    # special cases....
    if play_info.get("kicking_fgmissed", 0):
        play_type = str(play_type) + " MISSED"
    if "defense_sk_yds" in play_info:
        play_type = "sack"

    if "penalty" in play_info:
        play_type = "penalty"

    if "defense_int" in play_info:
        play_type = "interception"

    if "timeout" in play_info:
        play_type = "timeout"

        play.yardline['offset'] = 0

    if "touchdown" in play_info:
        if play_info["touchdown"]:
            points = "6 points"
            play_type = str(play_type) + " touchdown ({0})".format(points)

    if "fumbles_tot" in play_info:
        if play_info.get('fumbles_lost', None):
            play_type = str(play_type) + " FUMBLE LOST"
        else:
            play_type = str(play_type) + " FUMBLE RECOVERED"

    if "kicking_xpa" in play_info:
        if play_info["kicking_xpmade"]:
            play_type = "extra point (1 point)"
        else:
            play_type = "extra point (FAILED)"

    if not play_type:
        print play_info
    return play_type


def get_yards_gained(play):
    """
        given a play returns the number of yards
    """
    legend = {
        "rush": play.rushing_yds,
        "pass": play.passing_yds,
        "kick": play.kicking_yds,
        "punt": play.punting_yds,
        "sack": play.defense_sk_yds,
        "penalty": -play.penalty_yds,
        "field_goal": play.kicking_fgm_yds,
        "interception": play.defense_int_yds,
        "timeout": 3,
    }
    if play.type == "timeout":
        play.offset = 0
    if play.type:
        if len(play.type) > 1:
            yards = legend.get(play.type.split()[0], None)
        else:
            yards = legend.get(play.type, None)
    else:
        yards = 0
        print play
        play.type = "EOG"

    if not yards:
        print play.type

    return yards


def clean_drive_data(drive):
    """
        extracts meaningful data from drive and returns a dictionary
        - this list may need to be trimmed down or expanded

        input:
            nflgame.drive
        returns:
            a dictionary with all the desired drive info
    """
    drive_info = {
        'field_start': drive.field_start.__dict__,
        'field_end': drive.field_end.__dict__,
        'drive_num': drive.drive_num,
        'first_downs': drive.first_downs,
        'penalty_yds': drive.penalty_yds,
        'play_cnt': drive.play_cnt,
        'pos_time': drive.pos_time.__dict__,
        'result': drive.result,
        'team': drive.team,
        'total_yds': drive.total_yds
    }
    return drive_info


def drive_to_json(year, week, game, drive):
    """
        combines play and drive info
        input:
            year (str)
            week (int [0-16])
            game (int)
        return:
            json({plays: {}, drives: {}})
        TODO:
            HANDLE INVALID INPUT
   """
    tag = '<br>'
    games = get_games(year, week)
    if not games:
        games = get_games("2013", 5)
    drives = get_game_drives(games[game])
    drive = drives[drive]
    play_info = get_drive_plays(drive)
    drive_info = clean_drive_data(drive)
    fstart = 50 + drive_info['field_start']['offset']
    fend = 50+ drive_info['field_end']['offset']
    drive_str = "Team: {4}{5}Plays: {0}{5}First Downs: {2}{5}FieldStart: {6}{5}FieldEnd: {7}{5}Total Yards: {3}{5}Possesion: {1}{5}Result: {8}".format(
        drive_info['play_cnt'], drive_info['pos_time']['clock'], drive_info['first_downs'], drive_info['total_yds'], drive_info['team'],tag, fstart,fend, drive_info['result'])
    print drive_info
    drive_json = {'plays': play_info, 'drive': drive_str}
    return json.dumps(drive_json)


def get_game_drive_json(year, week, game):
    """
        given year, week and game returns all drives
    """
    data = {}
    drive_info = []
    games = get_games(year, week)
    if not games:
        games = get_games("2013", 5)
    drives = get_game_drives(games[game])
    for drive in drives:
        drive_info.append(
            "{0}_{1}_{2}".format(
                drive.drive_num,
                drive.team,
                drive.result))

    data['drive_info'] = drive_info
    data['game_info'] = {'year': year, 'week': week, 'game': game}
    return json.dumps(data)
