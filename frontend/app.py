import streamlit as st
import requests
import time
import json

# ------------------ CONFIG ------------------
# The URL for your FastAPI backend. Make sure it is running on this port.
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="TypeMaster", page_icon="⌨️", layout="wide")
st.title("⌨️ TypeMaster - Typing Speed Test")

# Initialize session state variables if they don't exist
if 'user' not in st.session_state:
    st.session_state.user = None
if 'text_data' not in st.session_state:
    st.session_state.text_data = None
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

# ------------------ SIDEBAR FOR USER LOGIN ------------------
st.sidebar.header("User Profile")
if st.session_state.user:
    st.sidebar.success(f"Logged in as: {st.session_state.user['username']}")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())
else:
    with st.sidebar.form("login_form"):
        st.subheader("Login / Signup")
        username = st.text_input("Username")
        email = st.text_input("Email")
        full_name = st.text_input("Full Name (optional)")
        submitted = st.form_submit_button("Login / Signup")

        if submitted:
            # Explicitly check that username and email are not empty strings
            if not username.strip() or not email.strip():
                st.sidebar.error("Username and Email are required.")
            else:
                try:
                    response = requests.post(
                        f"{API_URL}/users/create",
                        json={"username": username, "email": email, "full_name": full_name}
                    )
                    response.raise_for_status() # Raise an exception for HTTP errors
                    st.session_state.user = response.json().get("user")
                    st.sidebar.success(f"Logged in as {username}!")
                except requests.exceptions.RequestException as e:
                    # In case of a 400 Bad Request, we can get more info
                    if e.response and e.response.status_code == 400:
                        try:
                            error_detail = e.response.json().get("detail", "Bad request.")
                            st.sidebar.error(f"Error: {error_detail}")
                        except json.JSONDecodeError:
                            st.sidebar.error("Bad Request: The data sent was invalid.")
                    else:
                        st.sidebar.error(f"Error connecting to backend: {e}")
                except (json.JSONDecodeError, KeyError) as e:
                    st.sidebar.error("Invalid response from backend. Please check the backend logs.")


# ------------------ MAIN APP CONTENT ------------------

if not st.session_state.user:
    st.info("Please log in or sign up in the sidebar to start a typing test.")
else:
    # --- Typing Test Section ---
    st.header("Start a New Test")
    difficulty = st.selectbox("Select Difficulty", ["easy", "medium", "hard"])
    
    start_test_button = st.button("Get a New Text")
    if start_test_button:
        st.session_state.show_results = False
        st.session_state.text_data = None
        st.session_state.start_time = None
        st.session_state.end_time = None

        try:
            response = requests.get(f"{API_URL}/texts/random/{difficulty}")
            response.raise_for_status()
            text_response = response.json()
            if text_response.get("success"):
                st.session_state.text_data = text_response["text"]
                st.session_state.start_time = time.time()
            else:
                st.error("No texts found for this difficulty. Please add some to the database.")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to the backend API. Please ensure it is running: {e}")
        except (json.JSONDecodeError, KeyError) as e:
            st.error("Invalid response from backend.")
    
    if st.session_state.text_data:
        st.markdown(f"**Difficulty:** _{st.session_state.text_data['difficulty'].capitalize()}_")
        st.markdown(f"**Text:**")
        st.code(st.session_state.text_data["content"], language="text")

        typed_text = st.text_area("Start typing here...", height=200, key="typed_text")
        
        # Simple WPM calculation as user types
        current_time = time.time()
        duration = current_time - st.session_state.start_time if st.session_state.start_time else 0
        wpm = (len(typed_text.split()) / duration) * 60 if duration > 0 and len(typed_text.split()) > 0 else 0
        st.info(f"Current WPM: {wpm:.2f}")

        if st.button("Submit Test"):
            st.session_state.end_time = time.time()
            st.session_state.show_results = True

    if st.session_state.show_results and st.session_state.text_data:
        original_text = st.session_state.text_data["content"]
        typed_text = st.session_state.typed_text

        # Prepare payload for backend
        payload = {
            "user_id": st.session_state.user["id"],
            "text_id": st.session_state.text_data["id"],
            "wpm": wpm,
            "accuracy": 0, # Placeholder, calculation handled by logic.py
            "mistakes": 0  # Placeholder, calculation handled by logic.py
        }
        
        # Submit results to backend and get final calculated metrics
        try:
            response = requests.post(f"{API_URL}/results/submit", json=payload)
            response.raise_for_status()
            result_data = response.json()
            if result_data.get("success"):
                st.balloons()
                st.success("Test submitted successfully!")
                st.markdown(f"**Your WPM:** {result_data['result']['wpm']:.2f}")
                st.markdown(f"**Accuracy:** {result_data['result']['accuracy']:.2f}%")
                st.markdown(f"**Mistakes:** {result_data['result']['mistakes']}")
            else:
                st.error("Failed to submit results. Please try again.")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to the backend API to submit results: {e}")


# ------------------ LEADERBOARD SECTION ------------------
st.markdown("---")
st.header("Global Leaderboard")
try:
    lb_res = requests.get(f"{API_URL}/leaderboard")
    lb_res.raise_for_status()
    data = lb_res.json()
    leaderboard = data.get("leaderboard", [])

    if leaderboard:
        st.table(leaderboard)
    else:
        st.info("Leaderboard is empty. Be the first to add a result!")

except requests.exceptions.RequestException:
    st.error("Could not fetch the leaderboard. Please ensure the backend is running.")
except (json.JSONDecodeError, KeyError):
    st.error("Invalid response from the backend when fetching leaderboard data.")
