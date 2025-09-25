from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Get the absolute path to the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from src.logic import TypeMaster

# ------------------- App Setup -------------------

app = FastAPI(title="TypeMaster API", version="1.0")

# ------------------- CORS Middleware -------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Creating a TypeMaster Instance (business logic)
type_master = TypeMaster()

# ------------------- Data Models -------------------

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None

class TextCreate(BaseModel):
    content: str
    difficulty: str

class ResultCreate(BaseModel):
    user_id: str
    text_id: str
    wpm: float
    accuracy: float
    mistakes: int

# ------------------- API Endpoints -------------------

@app.get("/")
def home():
    return {"message": "TypeMaster API is running"}

# ------------------- Users Endpoints -------------------

@app.post("/users/create")
def create_user(user: UserCreate):
    # Corrected variable name to match the database schema
    res = type_master.add_user(user.username, user.email, user.full_name)
    if res["success"]:
        return res
    raise HTTPException(status_code=400, detail=res["message"])

@app.get("/users")
def get_users():
    res = type_master.list_users()
    return res

@app.put("/users/{user_id}")
def update_user(user_id: str, user: UserUpdate):
    res = type_master.update_user(user_id, user.dict(exclude_none=True))
    if res["success"]:
        return res
    raise HTTPException(status_code=400, detail=res["message"])

@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    res = type_master.delete_user(user_id)
    if res["success"]:
        return res
    raise HTTPException(status_code=400, detail=res["message"])

# ------------------- Texts Endpoints -------------------

@app.post("/texts/create")
def create_text(text: TextCreate):
    res = type_master.add_text(text.content, text.difficulty)
    if res["success"]:
        return res
    raise HTTPException(status_code=400, detail=res["message"])

@app.get("/texts/random/{difficulty}")
def get_random_text(difficulty: str):
    res = type_master.get_random_text(difficulty)
    if res["success"]:
        return res
    raise HTTPException(status_code=404, detail=res["message"])

# ------------------- Results Endpoints -------------------

@app.post("/results/submit")
def submit_result(result: ResultCreate):
    res = type_master.save_result(
        result.user_id,
        result.text_id,
        result.wpm,
        result.accuracy,
        result.mistakes
    )
    if res["success"]:
        return res
    raise HTTPException(status_code=400, detail=res["message"])

@app.get("/results/{user_id}")
def get_user_results(user_id: str):
    res = type_master.get_user_results(user_id)
    return res

# ------------------- Leaderboard Endpoint -------------------

@app.get("/leaderboard")
def get_leaderboard(limit: int = 10):
    res = type_master.get_leaderboard(limit)
    return res
