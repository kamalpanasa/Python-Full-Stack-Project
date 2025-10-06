import streamlit as st
import time
import uuid
import requests
import json # Ensure json is available for safety

# ---------------- CONFIG (must be first Streamlit command) ----------------
st.set_page_config(page_title="TypeMaster", layout="centered")
BASE_API_URL = "https://python-full-stack-project-xps2.onrender.com"  # Ensure this matches your FastAPI port
# TIME_LIMIT removed (now completion-based)

# ---------------- HELPERS ----------------
def highlight_typed_text(reference: str, typed: str) -> str:
    """Renders the reference text with colors indicating correct/incorrect typing."""
    out = []
    # Compare up to the length of the reference text
    for i, ch in enumerate(reference):
        if i < len(typed):
            if typed[i] == ch:
                out.append(f'<span style="color:#4CAF50">{ch}</span>') # Green for correct
            else:
                out.append(f'<span style="color:#F44336; text-decoration:underline;">{ch}</span>') # Red underline for mistake
        else:
            out.append(f'<span style="color:#8a8a8a">{ch}</span>') # Grey for untyped
            
    # Add excess typed characters in red
    if len(typed) > len(reference):
        extras = typed[len(reference):]
        out.append(f'<span style="color:#F44336">{extras}</span>')
        
    return "".join(out)

def fetch_new_text_from_api(difficulty: str):
    """Fetches a random text passage based on difficulty from the backend."""
    try:
        r = requests.get(f"{BASE_API_URL}/texts/{difficulty}", timeout=3)
        r.raise_for_status()
        j = r.json()
        # Your API structure returns {"data": [{id:..., content:...}]}
        if isinstance(j, dict) and j.get("data") and isinstance(j["data"], list) and j["data"]:
            item = j["data"][0]
            content = item.get("content")
            if content and isinstance(content, str) and content.strip():
                return {"id": item.get("id"), "content": content.strip()}
    except Exception:
        pass
    return None

def save_result_to_api(payload: dict):
    """Sends the final result data to the backend for WPM/Accuracy calculation and saving."""
    try:
        # NOTE: Your backend (main.py) expects typed_text, reference_text, start_time, end_time
        r = requests.post(f"{BASE_API_URL}/results/", json=payload, timeout=3)
        r.raise_for_status()
        return True
    except Exception:
        return False

# ---------------- API HANDLERS ----------------

def handle_login(username):
    """Checks if user exists (simplified API check) and sets session state."""
    try:
        r = requests.get(f"{BASE_API_URL}/users/", timeout=3)
        r.raise_for_status()
        users = r.json().get("data", [])
        user_data = next((u for u in users if u.get("username") == username), None)
        
        if user_data:
            st.session_state["logged_in"] = True
            st.session_state["username"] = user_data["username"]
            st.session_state["user_id"] = user_data["id"]
            st.success(f"Logged in as {st.session_state['username']}!")
            st.rerun() # Rerun to refresh UI
        else:
            st.error("Login failed: User not found.")
    except Exception:
        st.error("Login failed. Ensure API is running.")

def handle_register(username, email, full_name):
    """Registers a new user via API and logs them in."""
    payload = {"username": username, "email": email, "full_name": full_name}
    try:
        r = requests.post(f"{BASE_API_URL}/users/", json=payload, timeout=3)
        r.raise_for_status()
        
        # Assume successful creation returns the user object, extract ID
        user_id = r.json().get("data", [{}])[0].get("id", str(uuid.uuid4()))
        
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["user_id"] = user_id
        st.success("Registered and logged in!")
        st.rerun() # Rerun to refresh UI
    except Exception as e:
        st.error(f"Registration failed. Username or email may already be in use.")

# ---------------- SESSION STATE ----------------
defaults = {
    "reference_text": "Click 'Start New Test' to generate a text.",
    "current_text_id": None,
    "test_active": False,
    "test_finished": False,
    "typed_text": "",
    "difficulty": "medium",
    "logged_in": False,
    "username": "Guest",
    "user_id": None,
    "start_time": None,
    "end_time": None,
    "wpm": 0.0,
    "accuracy": 100.0,
    "mistakes": 0,
    "progress": 0.0,
    "result_submitted": False # Track submission status
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if st.session_state["user_id"] is None:
    st.session_state["user_id"] = str(uuid.uuid4())

# ---------------- UI ----------------
st.title("⌨️ TypeMaster — Live Typing Test")
st.markdown(f"Current User: **{st.session_state['username']}**")

# Sidebar: login/register
with st.sidebar:
    st.header("👤 Account")
    if not st.session_state["logged_in"]:
        mode = st.radio("Mode", ["Login", "Register"], key="sidebar_mode")
        username_in = st.text_input("Username", key="sidebar_username")
        
        if mode == "Register":
            email_in = st.text_input("Email", key="sidebar_email")
            full_in = st.text_input("Full name (optional)", key="sidebar_fullname")
            if st.button("Register", key="sidebar_btn_register") and username_in.strip():
                handle_register(username_in.strip(), email_in, full_in)
        else: # Login
            # Note: Password is not used by your current db.py, so we skip reading it
            if st.button("Login", key="sidebar_btn_login") and username_in.strip():
                handle_login(username_in.strip())
    else:
        st.markdown(f"**{st.session_state['username']}**")
        if st.button("Logout", key="sidebar_btn_logout"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = "Guest"
            st.session_state["user_id"] = str(uuid.uuid4())
            st.success("Logged out.")
            st.rerun()

# Difficulty selector + Start button
col1, col2 = st.columns([3,1])
with col1:
    st.selectbox("Difficulty", ["easy", "medium", "hard"], index=["easy", "medium", "hard"].index(st.session_state.get("difficulty", "medium")), key="difficulty_select")
    st.session_state["difficulty"] = st.session_state["difficulty_select"]
with col2:
    if st.button("🚀 Start New Test", key="start_test"):
        # Reset state and fetch new text
        st.session_state["test_active"] = True
        st.session_state["test_finished"] = False
        st.session_state["typed_text"] = ""
        st.session_state["start_time"] = None
        st.session_state["end_time"] = None
        st.session_state["result_submitted"] = False # Reset submission flag
        
        # Fetch new text and update state
        item = fetch_new_text_from_api(st.session_state["difficulty"])
        if item:
            st.session_state["reference_text"] = item["content"]
            st.session_state["current_text_id"] = item["id"]
        # Fallback is handled inside fetch_new_text_from_api
        st.rerun() # Rerun to refresh input area

# Show reference text with live highlight during test
st.markdown("### Text to Type")
if st.session_state["test_active"] or st.session_state["test_finished"]:
    highlighted = highlight_typed_text(st.session_state["reference_text"], st.session_state["typed_text"])
    st.markdown(
        f'<div style="border-radius:6px; padding:12px; background:#0f1113; color:#ddd; font-family:monospace; font-size:1.05em;">{highlighted}</div>',
        unsafe_allow_html=True,
    )
else:
    st.code(st.session_state["reference_text"])

# Typing input area
# The key must be the same as the session state variable name for simple reading/writing
typed = st.text_area(
    "Start typing here:",
    value=st.session_state["typed_text"],
    key="typed_text", # Critical: This key links directly to the session state variable
    height=170,
    placeholder="Type here...",
    disabled=not st.session_state["test_active"] or st.session_state["test_finished"],
)

# ---------------- LIVE METRICS CALCULATION AND DISPLAY ----------------

# The metric calculation logic relies entirely on reading st.session_state,
# which is updated by the text_area when a rerun occurs.

if st.session_state["test_active"]:
    # Read values from session state (updated by text_area and rerun loop)
    typed_text = st.session_state["typed_text"]
    ref_text = st.session_state["reference_text"]
    now = time.time()

    # Start timer on first keystroke
    if st.session_state["start_time"] is None and len(typed_text.strip()) > 0:
        st.session_state["start_time"] = now

    if st.session_state["start_time"]:
        duration = now - st.session_state["start_time"]
        
        # --- REMOVED: Time Limit Check ---
        
        if duration > 0:
            chars_typed = len(typed_text)
            wpm = (chars_typed / 5) / (duration / 60)
            correct_chars = sum(1 for a, b in zip(typed_text, ref_text) if a == b)
            mistakes = max(0, len(typed_text) - correct_chars)
            accuracy = (correct_chars / len(typed_text)) * 100 if len(typed_text) > 0 else 100.0
            progress = min(len(typed_text) / len(ref_text), 1.0)
        else:
            wpm, mistakes, accuracy, progress = 0, 0, 100, 0
    else:
        wpm, mistakes, accuracy, progress = 0, 0, 100, 0
    
    # Store live metrics back into session state
    st.session_state["wpm"] = wpm
    st.session_state["accuracy"] = accuracy
    st.session_state["mistakes"] = mistakes
    st.session_state["progress"] = progress

    # Check for completion (only completes when text matches exactly)
    if typed_text == ref_text and st.session_state["test_active"]:
        st.session_state["test_finished"] = True
        st.session_state["test_active"] = False
        st.session_state["end_time"] = time.time()
        
    # If test just finished, submit result
    if st.session_state["test_finished"] and not st.session_state.get("result_submitted", False):
        st.session_state["test_active"] = False # Ensure loop stops
        
        submit_payload = {
            "user_id": st.session_state["user_id"],
            "text_id": st.session_state["current_text_id"],
            "typed_text": typed_text,
            "reference_text": ref_text,
            "start_time": st.session_state["start_time"],
            "end_time": st.session_state["end_time"],
        }
        if save_result_to_api(submit_payload):
            st.session_state["result_submitted"] = True # Prevent resubmission
        
        st.success(f"Test complete! Final WPM: {st.session_state['wpm']:.2f} | Accuracy: {st.session_state['accuracy']:.1f}%")
        st.balloons()
    
    # Display live metrics
    col1, col2, col3, col4 = st.columns([1,1,1,1])
    col1.metric("WPM", f"{st.session_state['wpm']:.2f}")
    col2.metric("Accuracy", f"{st.session_state['accuracy']:.1f}%")
    col3.metric("Mistakes", st.session_state['mistakes'])
    
    # Display progress
    col4.progress(st.session_state['progress'])
    
    # --- CRITICAL FIX FOR LIVE TRACKING ---
    time.sleep(0.05)
    st.rerun()

# If the test is inactive or finished, display the last calculated metrics
elif st.session_state["test_finished"] or not st.session_state["test_active"]:
    col1, col2, col3, col4 = st.columns([1,1,1,1])
    col1.metric("WPM", f"{st.session_state['wpm']:.2f}")
    col2.metric("Accuracy", f"{st.session_state['accuracy']:.1f}%")
    col3.metric("Mistakes", st.session_state['mistakes'])
    
    # Display 0 progress or the final progress
    final_progress = st.session_state["progress"] if st.session_state.get("test_finished") else 0
    col4.progress(final_progress)


# Leaderboard 
st.markdown("---")
st.header("🏆 Leaderboard (top)")
try:
    r = requests.get(f"{BASE_API_URL}/leaderboard/", timeout=3)
    r.raise_for_status()
    lb = r.json().get("data", [])
    if lb:
        st.table(lb)
    else:
        st.info("Leaderboard empty or not available.")
except Exception:
    st.info("Leaderboard not available (backend not reachable or failed to parse data).")
