# chetnautils.py
# Utilities for Chetna: logs, language, complaints, voice/tts wrappers

import json
import os
import random
from datetime import datetime

# ----------- Logging -----------
CHAT_LOG = "logs/chetna_chat_history.txt"
COMPLAINTS_JSON = "logs/complaints.json"

def _ensure_dir(path):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def log_event(message: str):
    _ensure_dir(CHAT_LOG)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(CHAT_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {message}\n")

def log_chat(user, bot):
    log_event(f"USER: {user}")
    log_event(f"CHETNA: {bot}")

# ----------- Language & text helpers -----------
def detect_language(text: str) -> str:
    """
    Returns:
      'hi'       -> Hindi (Devanagari)
      'hi-latn'  -> Hinglish (Hindi in Latin script)
      'en'       -> English / default
    Heuristic: if any Devanagari char -> 'hi'
               else if enough Hindi markers in Latin -> 'hi-latn'
               else 'en'
    """
    if not text:
        return "en"

    # Devanagari range
    if any('\u0900' <= ch <= '\u097F' for ch in text):
        return "hi"

    t = text.lower().strip()

    # --- Tiny targeted fix: greetings typed in Latin should count as Hinglish ---
    hinglish_greeting_triggers = {
        "namaste", "namaskar", "pranam", "pranaam", "ram ram",
        "salaam", "salam", "adaab",
        "sat sri akaal", "satsriakaal", "satshriakal"
    }
    if any(g in t for g in hinglish_greeting_triggers):
        return "hi-latn"
    # ---------------------------------------------------------------------------

    # Compact list of common Hindi/Hinglish tokens
    markers = [
        "hai", "kya", "kyu", "kyun", "kab", "kaun", "kaise", "kidhar", "kahan",
        "se", "tak", "ke", "ka", "ki", "hona", "nikalti", "kiraya", "bus",
        "agla", "shaam", "subah", "rude", "shikayat", "complaint", "driver"
    ]
    score = sum(1 for w in markers if w in t)
    if score >= 2:
        return "hi-latn"
    return "en"

def normalize_text(text: str) -> str:
    return (text or "").strip()

def respond3(en: str, hi: str, hinglish: str, lang: str) -> str:
    """
    Pick the right response based on detected language.
    Falls back smartly if detection is confusing.
    """
    if lang == "en":
        return en
    elif lang == "hi":
        return hi
    elif lang == "hi-latn":
        # Prefer Hindi for Hinglish, unless Hinglish response is explicitly given
        return hinglish or hi
    else:
        # Default to English if detection failed
        return en


# Back-compat (en/hi only). If lang is hi-latn, we prefer Hindi here.
def respond(en_text: str, hi_text: str, lang: str = "en") -> str:
    if lang in ("hi", "hi-latn"):
        return hi_text
    return en_text


# ----------- Complaints -----------
def _load_complaints():
    if os.path.exists(COMPLAINTS_JSON):
        with open(COMPLAINTS_JSON, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def save_complaint_json(bus_number: str, complaint_text: str) -> str:
    _ensure_dir(COMPLAINTS_JSON)
    items = _load_complaints()
    ticket_id = f"C-{random.randint(1000, 9999)}"
    record = {
        "ticket_id": ticket_id,
        "bus_number": str(bus_number),
        "complaint": complaint_text,
        "time": datetime.now().isoformat()
    }
    items.append(record)
    with open(COMPLAINTS_JSON, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    log_event(f"COMPLAINT: {record}")
    return ticket_id

# ----------- Status / Delay -----------
def get_bus_delay_minutes(bus_number: str) -> int:
    # Simulated delay (0..20 mins). Could be replaced by real feed later.
    import random as _r
    _r.seed(int(''.join(ch for ch in str(bus_number) if ch.isdigit()) or "0"))
    return _r.randint(0, 20)

# ----------- Voice availability & TTS -----------
def voice_available() -> bool:
    try:
        import vosk  # noqa: F401
        import pyaudio  # noqa: F401
        return True
    except Exception:
        return False

def tts_available() -> bool:
    try:
        import pyttsx3  # noqa: F401
        return True
    except Exception:
        return False

def say(text: str):
    try:
        import pyttsx3
        engine = pyttsx3.init()
        # Optional: select a female-ish voice if available
        voices = engine.getProperty("voices")
        for v in voices:
            name = (v.name or "").lower()
            if "female" in name or "zira" in name or "heera" in name or "susan" in name:
                engine.setProperty("voice", v.id)
                break
        engine.setProperty("rate", 170)
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass

