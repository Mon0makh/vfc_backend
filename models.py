from pydantic import BaseModel

from typing import List, Union


class JumpRes(BaseModel):
    player_id: int
    jump_height: int

class DribRes(BaseModel):
    player_id: int
    time: int
    cone: int
class AccuRes(BaseModel):
    player_id: int
    hits: int

class PassRes(BaseModel):
    player_id: int
    hits: int


class Player(BaseModel):
    name: str
    last_name: str
    photo_url: str
    phone_number: str
    email: str
    player_number: int
    gender: str
    register_point: int
    player_height: int

class PlayerResultTry(BaseModel):
    match_id: int
    player_id: str
    game_id: int
    result: int

class UniqData(BaseModel):
    email: str
    phone: str


class BaseMatch:
    match_id: int
    players: {}
    match_status: bool
    match_stage: int


class PlayerResultGame(BaseModel):
    match_id: int
    player_id: str
    game_number: int
    result_list: List[str]


# START AUTH MODELS
class Token(BaseModel):
    access_token: str
    token_type: str
    expires: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str

# END AUT MODELS
