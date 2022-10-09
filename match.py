from datetime import datetime

from models import Player, JumpRes, AccuRes, DribRes, PassRes, BaseMatch
from connect_db import db_get_active_match, db_get_match_count, db_add_match, db_add_player_result_to_match, \
    db_update_player_list, db_get_player_by_id, db_del_player_from_match, db_edit_player_status, \
    db_update_player_jump_result, db_update_player_dribbling_result, db_update_player_accuracy_result, db_add_match, \
    db_update_player_pass_result
from config import GamesSetting


class Match():
    def __init__(self):
        self.id = db_get_match_count() + 1
        self.start_time = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
        self.progress = 0
        self.isFinished = False
        self.players = []
        self.players_json = {}
        db_add_match(self.id, self.start_time)

    def add_player_to_match(self, player_id: int):
        if player_id in self.players:
            return self.get_match_json("PLAYER HAS ADDED IN MATCH")

        if len(self.players) >= GamesSetting.GAMES_COUNT:
            return self.get_match_json("MAX PLAYERS!")

        player = db_get_player_by_id(player_id)
        if player is None:
            return self.get_match_json("PLAYER NOT FOUND!")

        if player.get('status') is not None and player.get('status') != 0:
            return self.get_match_json("PLAYER HAVE PLAY TODAY!")

        self.players.append(player_id)
        self.players_json[player_id] = player

        db_edit_player_status(player_id, 1)
        if db_update_player_list(self.id, self.players) is False:
            return self.get_match_json("ERROR CONNECT TO DB!")
        return self.get_match_json()

    # progress : "1/3"

    def del_player(self, player_id: int):
        if player_id in self.players:
            self.players.remove(player_id)
            self.players_json.pop(player_id)
            db_update_player_list(self.id, player_id)
        else:
            return self.get_match_json("Player not found!")

        return self.get_match_json()

    def get_match_json(self, msg="OK"):
        match_json = {
            "message": msg,
            "match_id": self.id,
            "players": self.players,
            "progress": self.progress,
            "finishIn": GamesSetting.progressMax(GamesSetting()),
        }
        return match_json

    def get_match_result_json(self):
        match_result = {
            "id": self.id,
            "status": "active",
            "players": {}
        }

        for player in self.players:
            match_result['players'][player] = {
                "last_name": self.players_json[player]['last_name'],
                "player_number": self.players_json[player]['number'],
                "photo_url": self.players_json[player]['photo_url'],
                "jump": self.players_json[player]['jump_result'],
                "jump_progress": str(self.players_json[player]['jump_progress']) + "/" + str(GamesSetting.JUMP_TRY_COUNT),
                "dribbling": self.players_json[player]['dribbling_result'],
                "dribbling_progress": str(self.players_json[player]['dribbling_progress']) + "/" + str(
                    GamesSetting.DRIBBLING_TRY_COUNT),
                "accuracy": self.players_json[player]['accuracy_result'],
                "accuracy_progress": str(self.players_json[player]['accuracy_progress']) + "/" + str(
                    GamesSetting.ACCURACY_TRY_COUNT),
                "pass": self.players_json[player]['pass_result'],
                "pass_progress": str(self.players_json[player]['pass_progress']) + "/" + str(
                    GamesSetting.PASS_TRY_COUNT),
                "match_score": self.players_json[player]['match_score']
            }
        return match_result

    def get_match_progress_json(self):
        match_result = {
            "id": self.id,
            "status": "active",
        }
        for player in self.players:
            match_result[player] = {
                "last_name": self.players_json[player]['last_name'],
                "player_number": self.players_json[player]['number'],
                "photo_url": self.players_json[player]['photo_url'],
                "jump_progress": self.players_json[player]['jump_progress'] + "/" + GamesSetting.JUMP_TRY_COUNT,
                "dribbling_progress": self.players_json[player][
                                          'dribbling_progress'] + "/" + GamesSetting.DRIBBLING_TRY_COUNT,
                "accuracy_progress": self.players_json[player][
                                         'accuracy_progress'] + "/" + GamesSetting.ACCURACY_TRY_COUNT,
                "pass_progress": self.players_json[player]['pass_progress'] + "/" + GamesSetting.PASS_TRY_COUNT,
            }
        return match_result

    def get_jump_setting(self):
        setting = {
            "try_count": GamesSetting.JUMP_TRY_COUNT,
            "max_score": 100
        }
        return setting

    def get_dribbling_setting(self):
        setting = {
            "try_count": GamesSetting.DRIBBLING_TRY_COUNT,
            "cone_fine": GamesSetting.DRIBBLING_CONE_FINE,
            "max_cone_count": GamesSetting.DRIBBLING_MAX_CONE_COUNT,
            "max_score": 100
        }
        return setting

    def get_accuracy_setting(self):
        setting = {
            "try_count": GamesSetting.ACCURACY_TRY_COUNT,
            "kick_count": GamesSetting.ACCURACY_KICK_COUNT,
            "max_score": 100
        }
        return setting

    def get_pass_setting(self):
        setting = {
            "try_count": GamesSetting.ACCURACY_TRY_COUNT,
            "max_score": 100
        }
        return setting

    def post_jump_result(self, jr: JumpRes):
        if jr.player_id in self.players:
            jump_progress = self.players_json[jr.player_id]['jump_progress']
            if jump_progress < GamesSetting.JUMP_TRY_COUNT:
                self.progress += 1
                self.players_json[jr.player_id]['jump_progress'] = jump_progress + 1
                if self.players_json[jr.player_id]['jump_result'] < jr.jump_height:
                    self.players_json[jr.player_id]['jump_result'] = jr.jump_height
                db_update_player_jump_result(jr.player_id, self.players_json[jr.player_id]['jump_result'],
                                             self.players_json[jr.player_id]['jump_progress'])
                return self.get_match_json(str(self.players_json[jr.player_id]['jump_progress']) + "/" + str(GamesSetting.JUMP_TRY_COUNT))
            else:
                return self.get_match_json("Исчерпано количество попыток!")
        else:
            return self.get_match_json("Некорректный ID Игрока!")

    def post_dribbling_result(self, dr: DribRes):
        if dr.player_id in self.players:
            drib_progress = self.players_json[dr.player_id]['dribbling_progress']

            if drib_progress < GamesSetting.DRIBBLING_TRY_COUNT:
                self.progress += 1
                self.players_json[dr.player_id]['dribbling_progress'] = drib_progress + 1
                if (self.players_json[dr.player_id]['dribbling_result'] > dr.time + dr.cone * 2) or (drib_progress == 0):
                    self.players_json[dr.player_id]['dribbling_result'] = dr.time + dr.cone * 2
                db_update_player_dribbling_result(dr.player_id, self.players_json[dr.player_id]['dribbling_result'],
                                                  self.players_json[dr.player_id]['dribbling_progress'])
                return self.get_match_json(str(self.players_json[dr.player_id]['dribbling_progress']) + "/" + str(GamesSetting.DRIBBLING_TRY_COUNT))
            else:
                return self.get_match_json("Исчерпано количество попыток!")

    def post_accuracy_result(self, ar: AccuRes):
        accu_progress = self.players_json[ar.player_id]['accuracy_progress']

        if accu_progress < GamesSetting.ACCURACY_TRY_COUNT:
            self.progress += 1
            self.players_json[ar.player_id]['accuracy_progress'] = accu_progress + 1
            if self.players_json[ar.player_id]['accuracy_result'] < ar.hits:
                self.players_json[ar.player_id]['accuracy_result'] = ar.hits
            db_update_player_accuracy_result(ar.player_id, self.players_json[ar.player_id]['accuracy_result'],
                                             self.players_json[ar.player_id]['accuracy_progress'])
            return self.get_match_json(str(self.players_json[ar.player_id]['accuracy_progress']) + "/" + str(GamesSetting.ACCURACY_TRY_COUNT))
        else:
            return self.get_match_json("Исчерпано количество попыток!")

    def post_pass_result(self, pr: PassRes):
        pass_progress = self.players_json[pr.player_id]['pass_progress']

        if pass_progress < GamesSetting.PASS_TRY_COUNT:
            self.progress += 1
            self.players_json[pr.player_id]['pass_progress'] = pass_progress + 1
            if self.players_json[pr.player_id]['pass_result'] < pr.hits:
                self.players_json[pr.player_id]['pass_result'] = pr.hits
            db_update_player_pass_result(pr.player_id, self.players_json[pr.player_id]['pass_result'],
                                         self.players_json[pr.player_id]['pass_progress'])
            return self.get_match_json(str(self.players_json[pr.player_id]['pass_progress']) + "/" + str(GamesSetting.PASS_TRY_COUNT))
        else:
            return self.get_match_json("Исчерпано количество попыток!")
