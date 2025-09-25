import time
from src import db

class TypeMaster:
    """
    Acts as a bridge between the frontend (Streamlit/FastAPI) and the database.
    It handles high-level business logic, performs data validation, and calls
    the appropriate functions from the database access layer (db.py).
    """

    def __init__(self):
        pass

    # ----------------- USERS -----------------

    def add_user(self, username, email, full_name):
        """Adds a new user to the database with validation."""
        if not username or not email:
            return {"success": False, "message": "Username and email are required"}
        
        result = db.create_user(username, email, full_name)

        if result and hasattr(result, 'data') and result.data:
            return {"success": True, "message": "User added successfully!", "user": result.data[0]}
        
        # Check if the result is a dictionary and contains an error
        if isinstance(result, dict) and result.get("error"):
            return {"success": False, "message": f"Error: {result.get('error')}"}

        return {"success": False, "message": "Unknown error occurred while creating user."}

    def list_users(self):
        """Fetches all users from the database."""
        result = db.get_all_users()
        if result and hasattr(result, 'data') and result.data:
            return {"success": True, "users": result.data}

        if isinstance(result, dict) and result.get("error"):
            return {"success": False, "message": f"Error: {result.get('error')}"}

        return {"success": False, "message": "Unknown error occurred while listing users."}

    def update_user(self, user_id, new_data: dict):
        """Updates a user's information by their ID."""
        result = db.update_user(user_id, new_data)
        if result and hasattr(result, 'data') and result.data:
            return {"success": True, "message": "User updated", "user": result.data[0]}
        
        if isinstance(result, dict) and result.get("error"):
            return {"success": False, "message": f"Error: {result.get('error')}"}

        return {"success": False, "message": "Error updating user."}

    def delete_user(self, user_id):
        """Deletes a user by their ID."""
        result = db.delete_user(user_id)
        if result and hasattr(result, 'data') and result.data:
            return {"success": True, "message": "User deleted"}
        
        if isinstance(result, dict) and result.get("error"):
            return {"success": False, "message": f"Error: {result.get('error')}"}

        return {"success": False, "message": "Error deleting user."}

    # ----------------- TEXTS -----------------

    def add_text(self, content, difficulty):
        """Inserts a new typing passage into the database."""
        if not content or not difficulty:
            return {"success": False, "message": "Content and difficulty are required"}

        result = db.create_text(content, difficulty)
        if result and hasattr(result, 'data') and result.data:
            return {"success": True, "message": "Text added successfully!", "text": result.data[0]}
        
        if isinstance(result, dict) and result.get("error"):
            return {"success": False, "message": f"Error: {result.get('error')}"}

        return {"success": False, "message": "Unknown error occurred while adding text."}

    def get_random_text(self, difficulty):
        """Fetches one random passage from the database based on difficulty."""
        result = db.get_random_text(difficulty)
        
        if result and hasattr(result, 'data') and result.data:
            if len(result.data) > 0:
                return {"success": True, "text": result.data[0]}
            else:
                return {"success": False, "message": "No texts found for this difficulty."}
        
        if isinstance(result, dict) and result.get("error"):
            return {"success": False, "message": f"Error: {result.get('error')}"}

        return {"success": False, "message": "No texts found."}

    # ----------------- RESULTS -----------------

    def save_result(self, user_id, text_id, wpm, accuracy, mistakes):
        """Saves a user's typing test result."""
        if not user_id or not text_id:
            return {"success": False, "message": "User ID and Text ID are required"}
        
        result = db.create_result(user_id, text_id, wpm, accuracy, mistakes)
        if result and hasattr(result, 'data') and result.data:
            return {"success": True, "message": "Result saved!", "result": result.data[0]}
        
        if isinstance(result, dict) and result.get("error"):
            return {"success": False, "message": f"Error: {result.get('error')}"}

        return {"success": False, "message": "Error saving result."}

    def get_user_results(self, user_id):
        """Fetches all results for a specific user."""
        result = db.get_user_results(user_id)
        if result and hasattr(result, 'data') and result.data:
            return {"success": True, "results": result.data}

        if isinstance(result, dict) and result.get("error"):
            return {"success": False, "message": f"Error: {result.get('error')}"}
        
        return {"success": False, "message": "Error fetching user results."}

    # ----------------- LEADERBOARD -----------------

    def get_leaderboard(self, limit=10):
        """Returns the top users for the leaderboard based on WPM."""
        result = db.get_leaderboard(limit)
        if result and hasattr(result, 'data') and result.data:
            return {"success": True, "leaderboard": result.data}

        if isinstance(result, dict) and result.get("error"):
            return {"success": False, "message": f"Error: {result.get('error')}"}

        return {"success": False, "message": "Error fetching leaderboard."}
