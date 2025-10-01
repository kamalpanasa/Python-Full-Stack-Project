import os
import random
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)


# ---------------- USERS TABLE OPERATIONS ---------------- #

def create_user(username, email, full_name=None):
    try:
        return supabase.table("users").insert({
            "username": username,
            "email": email,
            "full_name": full_name
        }).execute()
    except Exception as e:
        return {"data": None, "error": str(e)}

def get_all_users():
    try:
        return supabase.table("users").select("*").order("username").execute()
    except Exception as e:
        return {"data": None, "error": str(e)}

def update_user(user_id, new_data: dict):
    try:
        return supabase.table("users").update(new_data).eq("id", user_id).execute()
    except Exception as e:
        return {"data": None, "error": str(e)}

def delete_user(user_id):
    try:
        return supabase.table("users").delete().eq("id", user_id).execute()
    except Exception as e:
        return {"data": None, "error": str(e)}

def get_user_by_username(username):
    try:
        return supabase.table("users").select("*").eq("username", username).execute()
    except Exception as e:
        return {"data": None, "error": str(e)}


# ---------------- TEXTS TABLE OPERATIONS ---------------- #

def create_text(content, difficulty, language="English"):
    try:
        return supabase.table("texts").insert({
            "content": content,
            "difficulty": difficulty,
            "language": language
        }).execute()
    except Exception as e:
        return {"data": None, "error": str(e)}

def get_random_text(difficulty="easy"):
    try:
        res = supabase.table("texts").select("*").eq("difficulty", difficulty).execute()
        if not res.data:
            return {"data": [], "error": None}
        return {"data": [random.choice(res.data)], "error": None}
    except Exception as e:
        return {"data": [], "error": str(e)}

def get_all_texts():
    try:
        return supabase.table("texts").select("*").order("created_at", desc=True).execute()
    except Exception as e:
        return {"data": [], "error": str(e)}


# ---------------- RESULTS TABLE OPERATIONS ---------------- #

def create_result(user_id, text_id, wpm, accuracy, mistakes, duration):
    try:
        return supabase.table("results").insert({
            "user_id": user_id,
            "text_id": text_id,
            "wpm": wpm,
            "accuracy": accuracy,
            "mistakes": mistakes,
            "duration": duration
        }).execute()
    except Exception as e:
        return {"data": None, "error": str(e)}

def get_user_results(user_id):
    try:
        return supabase.table("results").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    except Exception as e:
        return {"data": [], "error": str(e)}


# ---------------- LEADERBOARD ---------------- #

def get_leaderboard(limit=10):
    try:
        return supabase.table("leaderboard").select("*").limit(limit).execute()
    except Exception as e:
        return {"data": [], "error": str(e)}
