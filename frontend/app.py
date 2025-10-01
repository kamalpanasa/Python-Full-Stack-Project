import streamlit as st
import time
import uuid
import requests

# ---------------- CONFIG (must be first Streamlit command) ----------------
st.set_page_config(page_title="TypeMaster", layout="centered")
BASE_API_URL = "http://localhost:8000"  # Change to your backend url if needed

# ---------------- HELPERS ----------------
def highlight_typed_text(reference: str, typed: str) -> str:
    out = []
    for i, ch in enumerate(reference):
        if i < len(typed):
            if typed[i] == ch:
                out.append(f'<span style="color:#4CAF50">{ch}</span>')
            else:
                out.append(f'<span style="color:#F44336; text-decoration:underline;">{ch}</span>')
        else:
            out.append(f'<span style="color:#8a8a8a">{ch}</span>')
    if len(typed) > len(reference):
        extras = typed[len(reference):]
        out.append(f'<span style="color:#F44336">{extras}</span>')
    return "".join(out)

def fetch_new_text_from_api(difficulty: str):
    try:
        r = requests.get(f"{BASE_API_URL}/texts/{difficulty}", timeout=3)
        r.raise_for_status()
        j = r.json()
        if isinstance(j, dict) and j.get("data"):
            item = j["data"][0]
            content = item.get("content")
            if content and isinstance(content, str) and content.strip():
                return {"id": item.get("id"), "content": content.strip()}
    except Exception:
        pass
    return None

def save_result_to_api(payload: dict):
    try:
        r = requests.post(f"{BASE_API_URL}/results/", json=payload, timeout=3)
        r.raise_for_status()
    except Exception:
        pass

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
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if st.session_state["user_id"] is None:
    st.session_state["user_id"] = str(uuid.uuid4())

# ---------------- UI ----------------
st.title("⌨️ TypeMaster — Live Typing Test")

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
                # Registration API call could be inserted here
                st.session_state["logged_in"] = True
                st.session_state["username"] = username_in.strip()
                st.success("Registered and logged in!")
        else:
            if st.button("Login", key="sidebar_btn_login") and username_in.strip():
                # Login API call could be inserted here
                st.session_state["logged_in"] = True
                st.session_state["username"] = username_in.strip()
                st.success(f"Logged in as {st.session_state['username']}")
    else:
        st.markdown(f"**{st.session_state['username']}**")
        if st.button("Logout", key="sidebar_btn_logout"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = "Guest"
            st.session_state["user_id"] = str(uuid.uuid4())
            st.success("Logged out.")

# Difficulty selector + Start button
col1, col2 = st.columns([3,1])
with col1:
    selected = st.selectbox("Difficulty", ["easy", "medium", "hard"], index=["easy", "medium", "hard"].index(st.session_state.get("difficulty", "medium")), key="difficulty_select")
    st.session_state["difficulty"] = selected
with col2:
    if st.button("🚀 Start New Test", key="start_test"):
        st.session_state["test_active"] = True
        st.session_state["test_finished"] = False
        st.session_state["typed_text"] = ""
        st.session_state["start_time"] = None
        st.session_state["end_time"] = None

        difficulty = st.session_state["difficulty"]
        item = fetch_new_text_from_api(difficulty)
        if item:
            st.session_state["reference_text"] = item["content"]
            st.session_state["current_text_id"] = item["id"]
        else:
            samples = {
                "easy": "The quick brown fox jumps over the lazy dog.",
                "medium": "A journey of a thousand miles begins with a single step.",
                "hard": "In programming, debugging is often twice as hard as writing the code."
            }
            st.session_state["reference_text"] = samples[difficulty]
            st.session_state["current_text_id"] = None

# Show reference text with live highlight during test
st.markdown("### Text to Type")
if st.session_state["test_active"]:
    highlighted = highlight_typed_text(st.session_state["reference_text"], st.session_state["typed_text"])
    st.markdown(
        f'<div style="border-radius:6px; padding:12px; background:#0f1113; color:#ddd; font-family:monospace; font-size:1.05em;">{highlighted}</div>',
        unsafe_allow_html=True,
    )
else:
    st.code(st.session_state["reference_text"])

# Typing input area - disabled when test inactive or finished
typed = st.text_area(
    "Start typing here:",
    value=st.session_state["typed_text"],
    key="typed_text",
    height=170,
    placeholder="Type here...",
    disabled=not st.session_state["test_active"] or st.session_state["test_finished"],
)

# Live metrics calculation
if st.session_state["test_active"]:
    if st.session_state["start_time"] is None and len(st.session_state["typed_text"].strip()) > 0:
        st.session_state["start_time"] = time.time()

    typed_text = st.session_state["typed_text"]
    ref_text = st.session_state["reference_text"]
    now = time.time()

    if st.session_state["start_time"]:
        duration = now - st.session_state["start_time"]
        if duration > 0:
            chars_typed = len(typed_text)
            wpm = (chars_typed / 5) / (duration / 60)
            correct_chars = sum(1 for a, b in zip(typed_text, ref_text) if a == b)
            mistakes = max(0, len(typed_text) - correct_chars)
            accuracy = (correct_chars / len(typed_text)) * 100 if len(typed_text) > 0 else 100.0
            progress = min(len(typed_text) / len(ref_text), 1.0)
        else:
            wpm = 0
            mistakes = 0
            accuracy = 100
            progress = 0
    else:
        wpm, mistakes, accuracy, progress = 0, 0, 100, 0

    # Display live metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("WPM", f"{wpm:.2f}")
    col2.metric("Accuracy", f"{accuracy:.1f}%")
    col3.metric("Mistakes", mistakes)
    col4.progress(progress)

    # Check for completion
    if typed_text == ref_text:
        st.session_state["test_finished"] = True
        st.session_state["test_active"] = False
        st.session_state["end_time"] = time.time()

        save_result_to_api({
            "user_id": st.session_state["user_id"],
            "text_id": st.session_state["current_text_id"],
            "typed_text": typed_text,
            "reference_text": ref_text,
            "start_time": st.session_state["start_time"],
            "end_time": st.session_state["end_time"],
        })
        st.success(f"Test complete! Final WPM: {wpm:.2f} | Accuracy: {accuracy:.1f}%")
        st.balloons()

# Leaderboard (optional)
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
    st.info("Leaderboard not available (backend not reachable).")

st.markdown("---")
