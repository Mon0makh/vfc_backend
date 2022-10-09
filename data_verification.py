from models import Player
from connect_db import db_add_player, db_get_player_by_id

def verify_player(player: Player):
    id = db_add_player(player)
    if id == "DNQ":
        return 400, "DNQ"
    elif id:
        return 200, str(id)

    return 500, "ERROR CONNECTION TO DB. DATA NOT SAVED!"


def verify_player_id(id: int):
    player = db_get_player_by_id(id)
    return player


# TODO
def verify_match_data(player: Player):
    pass