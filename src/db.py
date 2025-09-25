# db.py
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)


# ---------------- USERS TABLE OPERATIONS ---------------- #

# Create a new user
def create_user(username, email, full_name):
    return supabase.table("users").insert({
        "username": username,
        "email": email,
        "full_name": full_name
    }).execute()


# Get all users (ordered by username)
def get_all_users():
    return supabase.table("users").select("*").order("username").execute()


# Update user details
def update_user(user_id, new_data: dict):
    """
    new_data should be a dictionary of columns to update.
    Example: {"email": "new@email.com", "full_name": "New Name"}
    """
    return supabase.table("users").update(new_data).eq("id", user_id).execute()


# Delete a user
def delete_user(user_id):
    return supabase.table("users").delete().eq("id", user_id).execute()


# Get a single user by username
def get_user_by_username(username):
    return supabase.table("users").select("*").eq("username", username).execute()



# ---------------- TEXTS TABLE OPERATIONS ---------------- #

# Add a new text passage
def create_text(content, difficulty, language="English"):
    return supabase.table("texts").insert({
        "content": content,
        "difficulty": difficulty,
        "language": language
    }).execute()


# Get a random text by difficulty
def get_random_text(difficulty="easy"):
    return supabase.table("texts").select("*") \
        .eq("difficulty", difficulty) \
        .order("RANDOM()") \
        .limit(1) \
        .execute()


# Get all texts
def get_all_texts():
    return supabase.table("texts").select("*").order("created_at", desc=True).execute()



# ---------------- RESULTS TABLE OPERATIONS ---------------- #

# Insert a new result after a typing test
def create_result(user_id, text_id, wpm, accuracy, mistakes, duration):
    return supabase.table("results").insert({
        "user_id": user_id,
        "text_id": text_id,
        "wpm": wpm,
        "accuracy": accuracy,
        "mistakes": mistakes,
        "duration": duration
    }).execute()


# Get all results of a specific user
def get_results_by_user(user_id):
    return supabase.table("results").select("*") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .execute()


# Get best result of a user
def get_best_result_by_user(user_id):
    return supabase.table("results").select("wpm, accuracy") \
        .eq("user_id", user_id) \
        .order("wpm", desc=True) \
        .limit(1) \
        .execute()



# ---------------- LEADERBOARD ---------------- #

# Get top performers sorted by WPM
def get_leaderboard(limit=10):
    return supabase.table("results").select("user_id, wpm, accuracy") \
        .order("wpm", desc=True) \
        .limit(limit) \
        .execute()
