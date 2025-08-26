# chetna_loader.py
# Loads CSV/JSON datasets and provides search helpers for Chetna
# Also integrates GPT4All if available

import csv
import json
import os
import random
from datetime import datetime

# ---------- Try loading GPT4All ----------
try:
    from gpt4all import GPT4All
    _llm = GPT4All("ggml-gpt4all-j-v1.3-groovy")  # change model name if needed
    _llm_available = True
except Exception as e:
    _llm = None
    _llm_available = False


def llm_available():
    """Return True if GPT4All model loaded successfully"""
    return _llm_available


def ask_llm(prompt: str) -> str:
    """Send a prompt to GPT4All if available, else return fallback text"""
    if not _llm_available:
        return "LLM not available on this system."
    try:
        with _llm.chat_session():
            return _llm.generate(prompt, max_tokens=200)
    except Exception as e:
        return f"LLM error: {e}"


class ChetnaLoader:
    def __init__(self, file_path=None):
        self.file_path = file_path

    # ---------- Loaders ----------
    def load(self):
        if not self.file_path:
            return self._dummy()
        ext = os.path.splitext(self.file_path)[1].lower()
        if ext == ".json":
            return self.load_json()
        if ext == ".csv":
            return self.load_csv()
        return self._dummy()

    def load_json(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_csv(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def _dummy(self):
        return [
            {"bus_id": "202", "source": "Panipat", "destination": "Delhi", "time": "8:30 AM", "fare": "₹45"},
            {"bus_id": "702", "source": "Agra", "destination": "Lucknow", "time": "11:45 AM", "fare": "₹220"},
            {"bus_id": "1001", "source": "Delhi", "destination": "Dehradun", "time": "9:00 AM", "fare": "₹190"},
        ]

    # ---------- Helpers ----------
    @staticmethod
    def search_buses_by_number(buses, bus_number):
        for b in buses:
            if str(b.get("bus_id")) == str(bus_number):
                return b
        return None

    @staticmethod
    def buses_between(buses, src, dst):
        s, d = (src or "").lower(), (dst or "").lower()
        return [b for b in buses if b.get("source", "").lower() == s and b.get("destination", "").lower() == d]

    @staticmethod
    def _parse_time_12h(t):
        # "11:45 AM" -> datetime for sorting within same day
        try:
            return datetime.strptime(t.strip(), "%I:%M %p")
        except Exception:
            return datetime.strptime("12:00 AM", "%I:%M %p")

    def next_bus_between(self, buses, src, dst):
        matches = self.buses_between(buses, src, dst)
        if not matches:
            return None
        now = datetime.now()
        matches.sort(key=lambda b: self._parse_time_12h(b.get("time", "12:00 AM")))
        for b in matches:
            t = self._parse_time_12h(b.get("time", "12:00 AM"))
            if t.time() >= now.time():
                return b
        return matches[-1]  # fallback

    def last_bus_in_period_between(self, buses, src, dst, period):
        matches = self.buses_between(buses, src, dst)
        if not matches:
            return None

        def in_period(t, p):
            hour = self._parse_time_12h(t).hour
            if p == "morning":
                return 5 <= hour < 12
            if p == "afternoon":
                return 12 <= hour < 17
            if p == "evening":
                return 17 <= hour < 21
            if p == "night":
                return hour >= 21 or hour < 5
            return True

        period_matches = [b for b in matches if in_period(b.get("time", "12:00 AM"), period)]
        if not period_matches:
            return None
        period_matches.sort(key=lambda b: self._parse_time_12h(b.get("time", "12:00 AM")))
        return period_matches[-1]

    @staticmethod
    def simulate_bus_locations(buses):
        """
        Return dict: { bus_id: {location: "<stop/city>"} }
        """
        choices = {}
        for b in buses:
            bid = str(b.get("bus_id"))
            opts = [
                b.get("source", "City"), b.get("destination", "City"),
                "ISBT", "Bypass", "Main Road", "Kurukshetra", "Karnal", "Ambala", "Depot"
            ]
            choices[bid] = {"location": random.choice(opts)}
        return choices
