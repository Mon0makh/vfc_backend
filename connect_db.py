from pymongo import MongoClient
from datetime import datetime
from models import Player, BaseMatch

from config import MONGODB_LINK, MONGO_DB

mondb = MongoClient(MONGODB_LINK)[MONGO_DB]


def db_get_admin_login(login: str):
    try:
        user_db = mondb.admins.find_one({'username': login})
    except:
        # TODO LOGGING
        return None

    if user_db is not None:
        user = {
            "username": user_db['username'],
            "hashed_password": user_db['hashed_password'],
            "disabled": user_db['disabled']
        }
        return user

    else:
        return None


def db_get_player_phone(phone: str):
    try:
        player_phone = mondb.players.find_one({'phone_number': phone})
        if player_phone is not None:
            return player_phone
        else:
            return False
    except:
        return None


def db_get_player_email(email: str):
    try:
        player_email = mondb.players.find_one({'email': email})
        if player_email is not None:
            return player_email
        else:
            return False
    except:
        return None


def check_unique_reg(email: str, phone: str):
    email_data = db_get_player_email(email)
    phone_data = db_get_player_phone(phone)

    if email_data and phone_data:
        return False
    else:
        return True


def db_edit_player_status(id: int, status: int):
    try:
        player_db = mondb.players.find_one({'player_id': id})
        player_db['status'] = status
        mondb.players.update_one({'player_id': id}, {'$set': {'status': status}})
        return player_db
    except:
        return False


def db_get_player_by_id(id: int):
    try:
        player_db = mondb.players.find_one({'player_id': id})
        if player_db is not None:
            dict_player = {
                'player_id': player_db['player_id'],
                'name': player_db['name'],
                'last_name': player_db['last_name'],
                'photo_url': player_db['photo_url'],
                'number': player_db['number'],
                'player_height': player_db['player_height'],
                'jump_progress': player_db['jump_progress'],
                'jump_result': player_db['jump_result'],
                'dribbling_progress': player_db['dribbling_progress'],
                'dribbling_result': player_db['dribbling_result'],
                'accuracy_progress': player_db['accuracy_progress'],
                'accuracy_result': player_db['accuracy_result'],
                'pass_progress': player_db['pass_progress'],
                'pass_result': player_db['pass_result'],
                'match_score': player_db['match_score'],
            }
            return dict_player
        ## try:
    except:
        return {}



def db_get_match(id: int):
    try:
        match_db = mondb.matches.find_one({'match_id': id})
        if match_db is not None:
            match = {
                'match_id': match_db['match_id'],
                'players': match_db['players'],
            }
            return match
        return {}
    except:
        return {}


def db_all_matches():
    try:
        matches = mondb.matches.find({})

        all_matches = {}

        for match in matches:
            all_matches[match['match_id']] = {'players': match['players'], 'start_time': match['create_time']}
        return all_matches
    except:
        return {}

def db_add_player(player: Player):
    try:
        if check_unique_reg(player.email, player.phone_number):
            id = mondb.players.count_documents({}) + 1
            if player.register_point == 0:
                if id % 2 != 0:
                    id += 1
            else:
                if id % 2 == 0:
                    id += 1
            while True:
                haveId = mondb.players.find_one({"player_id": id})
                if haveId is not None:
                    id += 1
                    if player.register_point == 0:
                        if id % 2 != 0:
                            id += 1
                    else:
                        if id % 2 == 0:
                            id += 1
                else:
                    break

            dict_player = {
                'player_id': id,
                'name': player.name,
                'last_name': player.last_name,
                'photo_url': player.photo_url,
                'phone_number': player.phone_number,
                'email': player.email,
                'number': player.player_number,
                'gender': player.gender,
                'register_point': player.register_point,
                'player_height': player.player_height,
                'status': 0,
                'stage': 0,
                'now_playing': "",
                'jump_progress': 0,
                'jump_result': 0,
                'dribbling_progress': 0,
                'dribbling_result': 0,
                'accuracy_progress': 0,
                'accuracy_result': 0,
                'pass_progress': 0,
                'pass_result': 0,
                'match_score': 0,
                'create_time': datetime.now().strftime("%Y.%m.%d %H:%M:%S")
            }

            mondb.players.insert_one(dict_player)
            return id

        else:
            return "DNQ"

    except:
        # TODO LOGGING
        return False


def db_update_player_match_score(player_id: int):
    player = mondb.players.find_one({'player_id': player_id})
    if player is not None:
        score = 0
        jump_score = 0
        dribbling_score = 0
        accuracy_score = 0
        pass_score = 0
        if player['jump_result'] > 0:
            # if player['jump_result'] >= 60:
            #     jump_score = 100
            # else:
            #     jump_score = player['jump_result'] + 40
            _jump = player['jump_result'] - player['player_height']
            if _jump >= 60:
                jump_score = 100
            else:
                jump_score = _jump + 40

        if player['dribbling_result'] > 0:
            if player['dribbling_result'] < 8:
                dribbling_score = 100
            for i in range(20):
                if player['dribbling_result'] <= (8 + i * 2):
                    dribbling_score = (100 - i * 5)
                    break

        if player['accuracy_result'] > 0:
            if player['accuracy_result'] >= 7:
                accuracy_score = 100
            else:
                accuracy_score = 110 - 10 * (8 - player['accuracy_result'])

        if player['pass_result'] > 0:
            if player['pass_result'] <= 10:
                pass_score = player['pass_result'] * 10

        score = int((jump_score + dribbling_score + accuracy_score + pass_score) / 4)
        mondb.players.update_one({'player_id': player_id}, {'$set': {'match_score': score}})
        return score

def db_update_player_jump_result(player_id: int, jump: int, progress: int):
    try:
        mondb.players.update_one({'player_id': player_id}, {'$set': {'jump_result': jump, "jump_progress": progress}})
        # db_update_player_match_score(player_id)
        return True
    except:
      print("PLAYER NOT ADDED TO MATCH!")
      return False


def db_update_player_dribbling_result(player_id: int, time: int, progress: int):
    try:
        mondb.players.update_one({'player_id': player_id},
                                 {'$set': {'dribbling_result': time, "dribbling_progress": progress}})
        # db_update_player_match_score(player_id)
        return True
    except:
        print("PLAYER NOT ADDED TO MATCH!")
        return False


def db_update_player_accuracy_result(player_id: int, hits: int, progress: int):
    try:
        mondb.players.update_one({'player_id': player_id},
                                 {'$set': {'accuracy_result': hits, "accuracy_progress": progress}})
        # db_update_player_match_score(player_id)
        return True
    except:
        print("PLAYER NOT ADDED TO MATCH!")
        return False


def db_update_player_pass_result(player_id: int, score: int, progress: int):
    try:
        mondb.players.update_one({'player_id': player_id}, {'$set': {'pass_result': score, "pass_progress": progress}})
        # db_update_player_match_score(player_id)
        return True
    except:
        print("PLAYER NOT ADDED TO MATCH!")
        return False


## MATCHES
def db_add_match(match_id: int, time: str, ):
    try:
        match_json = {
            'match_id': match_id,
            'players': [],
            'progress': 0,
            'create_time': time
        }

        mondb.matches.insert_one(match_json)
        return True
    except:

        return False


def db_update_player_list(match_id: int, players: []):
    try:
        mondb.matches.update_one({'match_id': match_id}, {'$set': {'players': players}})
        return True
    except:
      print("PLAYER NOT ADDED TO MATCH!")
      return False


def db_del_player_from_match(match_id: int, player: str):
    try:
        match_db = mondb.matches.find_one({'match_id': match_id})
        match_db['players'].pop(player)
        mondb.matches.update_one({'_id': match_db['_id']}, {'$set': {'players': match_db['players']}})
        return match_db

    except:
        return False


def db_add_player_result_to_match(match_id: int, player_id: str, game_id: int, result: int):
    try:
        match_db = mondb.matches.find_one({'match_id': match_id})
        if match_db['players_result'].get(player_id) is None:
            match_db['players_result'][player_id] = {}
        match_db['players_result'][player_id][str(game_id)] = result
        mondb.matches.update_one({'_id': match_db['_id']}, {'$set': {'players_result': match_db['players_result']}})
        return match_db

    except:

        return False


def db_get_all_fresh_players():
    try:
        players_db = mondb.players.find({'status': 0})
        _players = []
        for player in players_db:
            _players.append(
                {'player_id': player['player_id'], 'name': player['name'], 'last_name': player['last_name']})
        return _players
    except:
        return {}


def db_get_active_match():
    try:
        match_db = mondb.matches.find_one({'match_status': True})
        print(match_db)
        return match_db
    except:
        return False


def db_find_match_by_id(id: int):
    try:
        match_db = mondb.matches.find_one({'match_id': id})
        return match_db
    except:
        return False


def db_get_match_count():
    try:
        count = mondb.matches.count_documents({})
        return count
    except:
        return False


async def check_players_update():
    change_stream = mondb["players"].watch()
    for _ in change_stream:
        yield True
    yield False
