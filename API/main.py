from fastapi import FastAPI
from pydantic import BaseModel
from src import db, logic

app = FastAPI(title="TypeMaster API")


# ------------------- Models ------------------- #

class User(BaseModel):
    username: str
    email: str
    full_name: str | None = None

class Result(BaseModel):
    user_id: str
    text_id: int
    typed_text: str
    reference_text: str
    start_time: float
    end_time: float


# ------------------- User Routes ------------------- #

@app.post("/users/")
def create_user(user: User):
    return db.create_user(user.username, user.email, user.full_name)

@app.get("/users/")
def get_users():
    return db.get_all_users()


# ------------------- Text Routes ------------------- #

@app.get("/texts/{difficulty}")
def get_text(difficulty: str):
    return db.get_random_text(difficulty)


# ------------------- Results Routes ------------------- #

@app.post("/results/")
def save_result(result: Result):
    res = logic.calculate_results(
        result.start_time,
        result.end_time,
        result.typed_text,
        result.reference_text
    )
    return db.create_result(
        result.user_id,
        result.text_id,
        res["wpm"],
        res["accuracy"],
        res["mistakes"],
        res["duration"]
    )

@app.get("/results/{user_id}")
def get_results(user_id: str):
    return db.get_user_results(user_id)


# ------------------- Leaderboard ------------------- #

@app.get("/leaderboard/")
def leaderboard(limit: int = 10):
    return db.get_leaderboard(limit)
