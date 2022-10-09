
# GAMES SETTINGS
class GamesSetting:
    GAMES_COUNT = 4

    JUMP_TRY_COUNT = 5
    JUMP_MAX_SCORE = 100

    DRIBBLING_TRY_COUNT = 3
    DRIBBLING_CONE_FINE = 2
    DRIBBLING_MAX_CONE_COUNT = 5
    DRIBBLING_MAX_SCORE = 100

    ACCURACY_TRY_COUNT = 2
    ACCURACY_KICK_COUNT = 7
    ACCURACY_MAX_SCORE = 100

    PASS_TRY_COUNT = 3
    PASS_MAX_SCORE = 10

    @staticmethod
    def progressMax(self):
        return self.GAMES_COUNT * (self.ACCURACY_TRY_COUNT + self.JUMP_TRY_COUNT + self.DRIBBLING_TRY_COUNT + self.PASS_TRY_COUNT)

# DB SETTING
MONGODB_LINK = "mongodb+srv://dev:D1675dOcw3qmkIKB@cluster0.zb1p3ac.mongodb.net/?retryWrites=true&w=majority"
MONGO_DB = "vfc"

# AUTHORIZATION SETTING
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

