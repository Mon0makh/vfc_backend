from fastapi import FastAPI, File, Depends, Form, WebSocket
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import PlainTextResponse
from fastapi.responses import Response, FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
import time
import uvicorn
import sys, logging
from datetime import datetime
from logging import StreamHandler, Formatter

from admin_auth import login_for_access_token, get_current_active_user
from models import Token, User, Player, PlayerResultTry, UniqData, JumpRes, AccuRes, DribRes, PassRes
from data_verification import verify_player, verify_player_id
from connect_db import check_unique_reg, check_players_update, db_all_matches, db_get_all_fresh_players
from match import Match
from bg_remove import remove_background

this_match = Match()



ALLOWED_ORIGINS = "*"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# handle CORS preflight requests
@app.options('/{rest_of_path:path}')
async def preflight_handler(request: Request, rest_of_path: str) -> Response:
    response = Response()
    response.headers['Access-Control-Allow-Origin'] = ALLOWED_ORIGINS
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
    return response



# set CORS headers
@app.middleware("http")
async def add_CORS_header(request: Request, call_next):
    response = await call_next(request)
    response.headers['Access-Control-Allow-Origin'] = ALLOWED_ORIGINS
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)


@app.get("/")
def read_root():
    return Response(content="Server OK", status_code=200)


@app.post("/OperatorSignIn", response_model=Token)
async def operator_login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await login_for_access_token(form_data)


@app.get("/users/me/", response_model=User)
async def get_read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.post("/add_player/")
async def post_add_player(id: int):
    return this_match.add_player_to_match(id)


@app.post("/delete_player/")
async def post_add_player(id: int):
    return this_match.del_player(id)


@app.get("/new_players/")
def get_new_players():
    return db_get_all_fresh_players()



@app.get("/match_player_result/")
async def post_match_player_result():
    return this_match.get_match_result_json()


@app.post("/register_new_player/")
async def post_register_player(player: Player):
    code, response_text = verify_player(player)
    return Response(content=response_text, status_code=code)


@app.get("/get_player/")
def get_player_by_id(id: int):
    print("!")
    player = verify_player_id(id)
    return player



@app.get("/match/")
def get_match_info():
    return this_match.get_match_json()

@app.get("/all_matches/")
def get_all_matches():
    return db_all_matches()

@app.websocket("/match_result/")
async def socket_match_result(websocket: WebSocket):
    await websocket.accept()
    while True:
        time.sleep(10)
        print(this_match.get_match_result_json())
        await websocket.send_json(this_match.get_match_result_json())

@app.get("/match_result/")
def get_match_result():
    return this_match.get_match_result_json()
@app.get("/start_new_match/")
def get_start_new_match():
   global this_match
   this_match = Match()
   print(this_match.get_match_json())
   print(this_match.get_match_result_json())
   return this_match.get_match_json("New match!")

@app.post("/jump_result/")
def post_jump_result(jr: JumpRes):
    return this_match.post_jump_result(jr)


@app.post("/dribbling_result/")
def post_jump_result(dr: DribRes):
    return this_match.post_dribbling_result(dr)

@app.post("/accuracy_result/")
def post_jump_result(ar: AccuRes):
    return this_match.post_accuracy_result(ar)

@app.post("/pass_result/")
def post_jump_result(pr: PassRes):
    return this_match.post_pass_result(pr)

@app.get("/jump_setting/")
def get_jump_setting():
    return this_match.get_jump_setting()


@app.get("/dribbling_setting/")
def get_dribbling_setting():
    return this_match.get_dribbling_setting()


@app.get("/accuracy_setting/")
def get_accuracy_setting():
    return this_match.get_accuracy_setting()

@app.get("/pass_setting/")
def get_accuracy_setting():
    return this_match.get_pass_setting()



@app.post("/upload_client_photo/{reg_stand}")
async def create_file(
        reg_stand: int,
        file: bytes = File()
):
    if file is None:
        return {"message": "No upload file sent"}
    else:
        path = "images/" + datetime.now().strftime("%d_%H_%M_%S_") + str(reg_stand) + ".png"
        with open(path, 'wb') as image:
            image.write(file)
            image.close()
        remove_background(path)
        return Response(content=path, status_code=200)


@app.post("/check_unique_data/")
def get_check_unique(uq: UniqData):
    return check_unique_reg(uq.email, uq.phone)


def main():
    this_match = Match()

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False, log_level="debug", debug=True)


if __name__ == "__main__":
    main()
