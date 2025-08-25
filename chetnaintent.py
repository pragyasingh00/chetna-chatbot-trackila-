# chetnaintent.py
# Robust intent + entity extraction, unified with chetnautils.detect_language

import re
from chetnautils import detect_language

# -----------------------------
# Helper extractors
# -----------------------------

BUS_RE = re.compile(r"\b(\d{2,4})\b")

def _extract_bus_number(text: str):
    m = BUS_RE.search(text)
    return m.group(1) if m else None

def _extract_route_entities(t: str):
    """
    Tries to grab source/destination from patterns like:
      - "from X to Y"
      - "X to Y"
      - "X se Y (tak|ke liye)" / "X se Y"
      - "X से Y तक"
    """
    text = " ".join(t.split())

    # English patterns
    m = re.search(r"(?:from\s+)?([a-zA-Z\u0900-\u097F]+)\s+to\s+([a-zA-Z\u0900-\u097F]+)", text)
    if m:
        return m.group(1), m.group(2)

    # Hinglish/Hindi (roman or Devanagari): "<X> se <Y> (tak|ke liye)?"
    m = re.search(r"([a-zA-Z\u0900-\u097F]+)\s+se\s+([a-zA-Z\u0900-\u097F]+)(?:\s+(?:tak|ke\s+liye))?", text)
    if m:
        return m.group(1), m.group(2)

    # Devanagari "से" / "तक"
    m = re.search(r"([a-zA-Z\u0900-\u097F]+)\s+से\s+([a-zA-Z\u0900-\u097F]+)(?:\s+तक)?", text)
    if m:
        return m.group(1), m.group(2)

    return None, None

def _extract_period(text: str):
    txt = text.lower()
    if any(w in txt for w in ["morning", "subah", "सुबह"]):
        return "morning"
    if any(w in txt for w in ["afternoon", "dopahar", "दोपहर"]):
        return "afternoon"
    if any(w in txt for w in ["evening", "shaam", "शाम"]):
        return "evening"
    if any(w in txt for w in ["night", "raat", "रात"]):
        return "night"
    return None

def _is_next_asked(text: str):
    txt = text.lower()
    return any(w in txt for w in ["next", "agla", "agli", "aagle"])

def _is_greeting(text: str):
    txt = text.lower()
    greetings = [
        r"\bhi\b", r"\bhello\b", r"\bhii\b", r"\bhey\b", r"\bhiii\b",
        r"\bnamaste\b", r"\bnamaskar\b", "नमस्ते", "नमस्कार"
    ]
    return any(re.search(g, txt) for g in greetings)

def _has_any(txt: str, words):
    low = txt.lower()
    return any(w in low for w in words)

# -----------------------------
# Main intent extractor
# -----------------------------

def get_intent(user_input: str) -> dict:
    """
    Returns a dict with:
      intent: one of [greetings, fare_info, timing_info, track_bus, status_info, route_info, lodge_complaint, unknown]
      lang: 'en' | 'hi' | 'hi-latn'
      bus_number?: str
      source?: str
      destination?: str
      period?: str
      ask_next?: bool
      complaint_text?: str
    """
    text = user_input.strip()
    low = text.lower()
    lang = detect_language(text)
    bus_number = _extract_bus_number(low)
    src, dst = _extract_route_entities(low)   # ✅ extracted only once here

    # 1) Greetings
    if _is_greeting(low):
        return {"intent": "greetings", "lang": lang}

    # 2) Fare
    if _has_any(low, ["fare", "kiraya", "price", "ticket", "किराया"]):
        return {"intent": "fare_info", "lang": lang, "bus_number": bus_number}

    # 3) Timing / schedule
    if _has_any(low, ["time", "timing", "schedule", "kab", "baje", "कब", "समय", "टाइम", "बजे"]):
        return {"intent": "timing_info", "lang": lang, "bus_number": bus_number}

    # 4) Track location
    if _has_any(low, [
        "track", "kidhar", "where", "kahan", "location",
        "कहाँ", "कहां", "abhi kaha hai", "bus kidhar hai",
        "se aane wali bus", "bus ka pata", "bus location"
    ]):
        return {
            "intent": "track_bus",
            "lang": lang,
            "bus_number": bus_number,
            "source": src,
            "destination": dst
        }

    # 5) Status (late/on-time)
    if _has_any(low, ["status", "on time", "ontime", "late", "delay", "delayed", "लेट", "देरी"]):
        return {"intent": "status_info", "lang": lang, "bus_number": bus_number}

     # 6) Complaint
    if _has_any(low, [
        "complaint", "shikayat", "issue", "problem",
        "rude", "driver", "bad", "ganda", "gandi", "gandi tarah",
        "misbehave", "not found", "missing", "unclean", "dirty",
        "बदतमीज", "शिकायत", "गंदा", "गंदी"
    ]):
        return {
            "intent": "lodge_complaint",
            "lang": lang,
            "bus_number": bus_number,
            "complaint_text": text
        }

    # 7) Route / search between cities
    if src and dst:
        return {
            "intent": "route_info",
            "lang": lang,
            "source": src.title(),
            "destination": dst.title(),
            "period": _extract_period(low),
            "ask_next": _is_next_asked(low),
        }

    # 8) Unknown (fallback)
    return {"intent": "unknown", "lang": lang}
