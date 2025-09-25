# src/logic.py

from src import db  # import functions from db.py


class TypeMaster:
    """
    Acts as a bridge between frontend (Streamlit/FastAPI) and the database.
    Handles business logic, validation, and calls DB operations.
    """

    def __init__(self):
        pass  # no instance variables needed since db handles connections

    # ----------------- USERS -----------------

    def add_user(self, username, email, full_name):
        """Add a new user with validation."""
        if not username or not email:
            return {"success": False, "message": "Username and email are required"}

        result = db.create_user(username, email, full_name)

        if result.data:
            return {"success": True, "message": "User added successfully!", "user": result.data[0]}
        return {"success": False, "message": f"Error: {result.error}"}

    def list_users(self):
        """Fetch all users."""
        result = db.get_all_users()
        return {"success": True, "users": result.data}

    def update_user(self, user_id, new_data: dict):
        """Update user info (username, email, full_name)."""
        result = db.update_user(user_id, new_data)
        if result.data:
            return {"success": True, "message": "User updated", "user": result.data[0]}
        return {"success": False, "message": "Error updating user"}

    def delete_user(self, user_id):
        """Delete a user by ID."""
        result = db.delete_user(user_id)
        if result.data:
            return {"success": True, "message": "User deleted"}
        return {"success": False, "message": "Error deleting user"}

    # ----------------- TEXTS -----------------

    def add_text(self, content, difficulty):
        """Insert a new typing passage."""
        if not content or not difficulty:
            return {"success": False, "message": "Content and difficulty are required"}

        result = db.create_text(content, difficulty)
        if result.data:
            return {"success": True, "message": "Text added successfully!", "text": result.data[0]}
        return {"success": False, "message": f"Error: {result.error}"}

    def get_random_text(self, difficulty):
        """Fetch one random passage by difficulty."""
        result = db.get_random_text(difficulty)
        if result.data:
            return {"success": True, "text": result.data[0]}
        return {"success": False, "message": "No texts found"}

    # ----------------- RESULTS -----------------

    def save_result(self, user_id, text_id, wpm, accuracy, mistakes):
        """Save a typing test result."""
        if not user_id or not text_id:
            return {"success": False, "message": "User ID and Text ID are required"}

        result = db.create_result(user_id, text_id, wpm, accuracy, mistakes)
        if result.data:
            return {"success": True, "message": "Result saved!", "result": result.data[0]}
        return {"success": False, "message": f"Error: {result.error}"}

    def get_user_results(self, user_id):
        """Fetch all results for a user."""
        result = db.get_user_results(user_id)
        return {"success": True, "results": result.data}

    # ----------------- LEADERBOARD -----------------

    def get_leaderboard(self, limit=10):
        """Return top users ordered by WPM."""
        result = db.get_leaderboard(limit)
        return {"success": True, "leaderboard": result.data}