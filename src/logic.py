import time

# ------------------- Typing Logic ------------------- #

def calculate_results(start_time, end_time, typed_text, reference_text):
    duration = round(end_time - start_time, 2)  # seconds
    words = len(typed_text.split())
    wpm = round((words / duration) * 60, 2) if duration > 0 else 0
    
    correct_chars = sum(1 for a, b in zip(typed_text, reference_text) if a == b)
    accuracy = round((correct_chars / len(reference_text)) * 100, 2) if reference_text else 0
    mistakes = max(len(reference_text) - correct_chars, 0)

    return {
        "wpm": wpm,
        "accuracy": accuracy,
        "mistakes": mistakes,
        "duration": duration
    }


# ------------------- Timer Utils ------------------- #

def start_timer():
    return time.time()

def stop_timer():
    return time.time()
