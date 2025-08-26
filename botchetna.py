# botchetna.py
# Chetna – Transport/Bus Chatbot (offline-first, voice & local LLM optional)

import os
import re
import sys
from chetnaintent import get_intent
from chetna_loader import ChetnaLoader
from chetnautils import (
    respond3, respond, detect_language, log_event, log_chat,
    save_complaint_json, get_bus_delay_minutes,
    voice_available, tts_available, say,
)
import json
from langdetect import detect   
import pyttsx3                         # for text-to-speech (Chetna’s female voice)
import speech_recognition as sr
# -------- Optional: GPT4All local LLM (used only if installed & available) --------
LOCAL_LLM_READY = False
LLM_MODEL = None
try:
    from gpt4all import GPT4All  # pip install gpt4all
    model_name = os.getenv("CHETNA_GPT4ALL_MODEL", "ggml-model-gpt4all-falcon-q4_0.bin")
    model_dir = os.getenv("CHETNA_GPT4ALL_MODELS", os.path.join(os.getcwd(), "models"))
    model_path = os.path.join(model_dir, model_name)
    if os.path.exists(model_path):
        LLM_MODEL = GPT4All(model_name=model_name, model_path=model_dir, allow_download=False)
        LOCAL_LLM_READY = True
except Exception:
    LOCAL_LLM_READY = False

def llm_fallback(prompt: str, lang: str) -> str:
    """
    Used when intent is unknown and a local GPT4All model is available.
    Language-aware: en / hi / hi-latn (Hinglish).
    """
    if not LOCAL_LLM_READY or LLM_MODEL is None:
        return ""
    if lang == "hi":
        target = "Hindi (Devanagari script)"
    elif lang == "hi-latn":
        target = "Hinglish (Hindi written in Latin script)"
    else:
        target = "English"
    system = (
        "You are Chetna, a polite female transport assistant. "
        f"Answer concisely in {target}, no emojis."
    )
    try:
        with LLM_MODEL.chat_session(system_prompt=system):
            out = LLM_MODEL.generate(prompt, max_tokens=256, temp=0.2)
        return (out or "").strip()
    except Exception:
        return ""

# ---------------- Data ----------------
DATA_PATH_JSON = "data/chetnasample_buses.json"
DATA_PATH_CSV  = "data/chetnasample_buses.csv"

loader = ChetnaLoader(DATA_PATH_JSON if os.path.exists(DATA_PATH_JSON) else DATA_PATH_CSV)
BUSES = loader.load()

# ---------------- Intro ----------------
print("Chetna started! Type 'help' for options and 'exit' to quit.")

def handle_intent(user_input: str):
    """
    Core dispatcher. Detects intent and returns (reply_text, speak_text).
    """
    intent_data = get_intent(user_input)
    intent = intent_data.get("intent", "unknown")
    lang = intent_data.get("lang") or detect_language(user_input)

    # 1) Greetings
    if intent == "greetings":
        msg = respond3(
            "Hello! I am Chetna. How can I help you with buses today?",
            "नमस्ते! मैं चेतना बोल रही हूँ। मैं आपकी बस से जुड़ी मदद कैसे कर सकती हूँ?",
            "Namaste! Main Chetna bol rahi hoon. Main aapki bus se judi madad kaise kar sakti hoon?",
            lang
        )
        return msg, msg

    # 2) Fare info
    if intent == "fare_info":
        bus_number = intent_data.get("bus_number")
        if not bus_number:
            msg = respond3(
                "Please tell me the bus number to check the fare.",
                "किराया बताने के लिए बस नंबर बताएँ।",
                "Kirpya kiraya batane ke liye bus number bataye.",
                lang
            )
            return msg, msg
        bus = loader.search_buses_by_number(BUSES, bus_number)
        if bus:
            msg = respond3(
                f"The fare for bus {bus_number} is {bus['fare']}.",
                f"बस {bus_number} का किराया {bus['fare']} है।",
                f"Bus {bus_number} ka kiraya {bus['fare']} hai.",
                lang
            )
        else:
            msg = respond3(
                f"Sorry, I could not find bus {bus_number}.",
                f"माफ़ कीजिए, मुझे बस {bus_number} नहीं मिली।",
                f"Maaf kijiye, mujhe bus {bus_number} nahi mili.",
                lang
            )
        return msg, msg

    # 3) Timing info
    if intent == "timing_info":
        bus_number = intent_data.get("bus_number")
        if not bus_number:
            msg = respond3(
                "Please tell me the bus number to check timing.",
                "टाइमिंग बताने के लिए बस नंबर बताएँ।",
                "Kirpya timing batane ke liye bus number bataye.",
                lang
            )
            return msg, msg
        bus = loader.search_buses_by_number(BUSES, bus_number)
        if bus:
            msg = respond3(
                f"Bus {bus_number} leaves at {bus['time']}.",
                f"बस {bus_number} {bus['time']} बजे निकलती है।",
                f"Bus {bus_number} {bus['time']} baje nikalti hai.",
                lang
            )
        else:
            msg = respond3(
                f"Sorry, I could not find bus {bus_number}.",
                f"माफ़ कीजिए, मुझे बस {bus_number} नहीं मिली।",
                f"Maaf kijiye, mujhe bus {bus_number} nahi mili.",
                lang
            )
        return msg, msg

    # 4) Track bus
    if intent == "track_bus":
        bus_number = intent_data.get("bus_number")
        if not bus_number:
            msg = respond3(
                "Please tell me the bus number to track.",
                "बस को ट्रैक करने के लिए बस नंबर बताएँ।",
                "Kirpya bus ko track karne ke liye bus number bataye.",
                lang
            )
            return msg, msg
        bus = loader.search_buses_by_number(BUSES, bus_number)
        if bus:
            loc_map = loader.simulate_bus_locations([bus])
            location = loc_map[str(bus_number)]["location"]
            msg = respond3(
                f"Bus {bus_number} is currently near {location}.",
                f"बस {bus_number} अभी {location} के पास है।",
                f"Bus {bus_number} abhi {location} ke paas hai.",
                lang
            )
        else:
            msg = respond3(
                f"Sorry, I could not find bus {bus_number}.",
                f"माफ़ कीजिए, मुझे बस {bus_number} नहीं मिली।",
                f"Maaf kijiye, mujhe bus {bus_number} nahi mili.",
                lang
            )
        return msg, msg

    # 5) Routes / Next / Period
    if intent == "route_info":
        src = intent_data.get("source")
        dst = intent_data.get("destination")
        period = intent_data.get("period")
        ask_next = intent_data.get("ask_next", False)

        if not (src and dst):
            msg = respond3(
                "Please provide both source and destination, e.g., 'buses from Delhi to Karnal'.",
                "कृपया स्रोत और गंतव्य दोनों बताएँ, जैसे: 'दिल्ली से करनाल की बसें'।",
                "Kirpya source aur destination dono bataye, jaise: 'Delhi se Karnal ki basen'.",
                lang
            )
            return msg, msg

        if ask_next:
            nb = loader.next_bus_between(BUSES, src, dst)
            if nb:
                msg = respond3(
                    f"Next bus from {src} to {dst} is {nb['bus_id']} at {nb['time']} with fare {nb['fare']}.",
                    f"{src} से {dst} के लिए अगली बस {nb['bus_id']} है, समय {nb['time']}, किराया {nb['fare']}।",
                    f"{src} se {dst} ke liye agla bus {nb['bus_id']} hai, samay {nb['time']}, kiraya {nb['fare']}.",
                    lang
                )
            else:
                msg = respond3(
                    f"I could not find the next bus from {src} to {dst}.",
                    f"माफ़ कीजिए, {src} से {dst} के लिए अगली बस नहीं मिली।",
                    f"Maaf kijiye, {src} se {dst} ke liye agla bus nahi mila.",
                    lang
                )
            return msg, msg

        if period:
            lb = loader.last_bus_in_period_between(BUSES, src, dst, period)
            if lb:
                msg = respond3(
                    f"The last {period} bus from {src} to {dst} is {lb['bus_id']} at {lb['time']}.",
                    f"{src} से {dst} के लिए {period} की आख़िरी बस {lb['bus_id']} है, समय {lb['time']}।",
                    f"{src} se {dst} ke liye {period} ki aakhri bus {lb['bus_id']} hai, samay {lb['time']}.",
                    lang
                )
            else:
                matches = loader.buses_between(BUSES, src, dst)
                if matches:
                    times = ", ".join([f'{b["bus_id"]} at {b["time"]}' for b in matches])
                    msg = respond3(
                        f"No specific {period} service. Available buses: {times}.",
                        f"विशेष {period} सेवा नहीं है। उपलब्ध बसें: {times}।",
                        f"Vishesh {period} seva nahi hai. Uplabdh basen: {times}.",
                        lang
                    )
                else:
                    msg = respond3(
                        f"No buses found between {src} and {dst}.",
                        f"{src} और {dst} के बीच कोई बस नहीं मिली।",
                        f"{src} aur {dst} ke beech koi bus nahi mili.",
                        lang
                    )
            return msg, msg

        matches = loader.buses_between(BUSES, src, dst)
        if matches:
            if lang == "hi":
                lines = [f"बस {b['bus_id']} {b['source']} से {b['destination']} के लिए {b['time']} बजे, किराया {b['fare']}।" for b in matches]
            elif lang == "hi-latn":
                lines = [f"Bus {b['bus_id']} {b['source']} se {b['destination']} ke liye {b['time']} baje, kiraya {b['fare']}." for b in matches]
            else:
                lines = [f"Bus {b['bus_id']} from {b['source']} to {b['destination']} at {b['time']} (fare {b['fare']})." for b in matches]
            msg = "\n".join(lines)
        else:
            nb = loader.next_bus_between(BUSES, src, dst)
            if nb:
                msg = respond3(
                    f"No direct listing found. Next bus from {src} to {dst} is {nb['bus_id']} at {nb['time']}.",
                    f"सीधी सूची नहीं मिली। {src} से {dst} की अगली बस {nb['bus_id']} है, समय {nb['time']}।",
                    f"Seedhi suchi nahi mili. {src} se {dst} ka agla bus {nb['bus_id']} hai, samay {nb['time']}.",
                    lang
                )
            else:
                msg = respond3(
                    f"No buses found between {src} and {dst}.",
                    f"{src} और {dst} के बीच कोई बस नहीं मिली।",
                    f"{src} aur {dst} ke beech koi bus nahi mili.",
                    lang
                )
        return msg, msg

    # 6) Status (delay/on-time)
    if intent == "status_info":
        bus_number = intent_data.get("bus_number")
        if not bus_number:
            msg = respond3(
                "Please tell me the bus number to check status.",
                "स्टेटस बताने के लिए बस नंबर बताएँ।",
                "Kirpya status batane ke liye bus number bataye.",
                lang
            )
            return msg, msg
        bus = loader.search_buses_by_number(BUSES, bus_number)
        if not bus:
            msg = respond3(
                f"Sorry, I could not find bus {bus_number}.",
                f"माफ़ कीजिए, मुझे बस {bus_number} नहीं मिली।",
                f"Maaf kijiye, mujhe bus {bus_number} nahi mili.",
                lang
            )
            return msg, msg
        delay = get_bus_delay_minutes(bus_number)
        if delay <= 0:
            msg = respond3(
                f"Bus {bus_number} is on time today.",
                f"बस {bus_number} आज समय पर है।",
                f"Bus {bus_number} aaj samay par hai.",
                lang
            )
        else:
            msg = respond3(
                f"Bus {bus_number} is running {delay} minutes late today.",
                f"बस {bus_number} आज {delay} मिनट लेट चल रही है।",
                f"Bus {bus_number} aaj {delay} minute late chal rahi hai.",
                lang
            )
        return msg, msg

    # 7) Complaints (rude/late/not found/driver etc.)
    if intent == "lodge_complaint":
        bus_number = intent_data.get("bus_number")
        complaint_text = intent_data.get("complaint_text") or user_input

        if not bus_number:
            msg = respond3(
                "Please mention the bus number in your complaint.",
                "कृपया अपनी शिकायत में बस नंबर ज़रूर बताएँ।",
                "Kirpya apni shikayat mein bus number zarur bataye.",
                lang
            )
            return msg, msg

        ticket_id = save_complaint_json(bus_number, complaint_text)

        msg = respond3(
            f"Your complaint has been logged. Ticket ID: {ticket_id}.",
            f"आपकी शिकायत दर्ज हो गई है। टिकट आईडी: {ticket_id}।",
            f"Aapki shikayat register ho gayi hai. Ticket ID: {ticket_id}.",
            lang
        )
        return msg, msg

    # 8) Fallbacks:
    # If user typed just a number like "702", show bus details
    bus_num_match = re.search(r"\b\d{2,4}\b", user_input)
    if bus_num_match:
        bus_number = bus_num_match.group()
        bus = loader.search_buses_by_number(BUSES, bus_number)
        if bus:
            msg = respond3(
                f"Bus {bus_number} goes from {bus['source']} to {bus['destination']} at {bus['time']} with fare {bus['fare']}.",
                f"बस {bus_number} {bus['source']} से {bus['destination']} जाती है, समय {bus['time']}, किराया {bus['fare']}।",
                f"Bus {bus_number} {bus['source']} se {bus['destination']} jati hai, samay {bus['time']}, kiraya {bus['fare']}.",
                lang
            )
            return msg, msg

    # If still unknown and local LLM exists, try answering generally
    if LOCAL_LLM_READY:
        llm_ans = llm_fallback(user_input, lang)
        if llm_ans:
            return llm_ans, llm_ans
# Final fallback
    # Final fallback with language detection
    try:
        lang = detect(user_input)
    except:
        lang = "en"   # default to English if detection fails

    if lang == "en":
        msg = "I am not sure I understood that. Please rephrase."
    elif lang == "hi":
        msg = "माफ़ कीजिए, मैं समझ नहीं पाई। कृपया दोबारा बताएँ।"
    else:
        msg = "Maaf kijiye, main samajh nahi payi. Kripya dobara bataye."

    return msg, msg


# ---------------- Optional Voice Input (Vosk) ----------------
USE_VOICE = voice_available()
USE_TTS = tts_available()

def listen_once():
    """
    If voice stack is available, capture one utterance and return text.
    Otherwise return ''.
    """
    if not USE_VOICE:
        return ""
    try:
        from vosk import Model, KaldiRecognizer
        import pyaudio, json, os
        model_dir = os.getenv("CHETNA_VOSK_MODEL", "models/vosk-model-small-en-us-0.15")
        if not os.path.exists(model_dir):
            return ""
        model = Model(model_dir)
        rec = KaldiRecognizer(model, 16000)

        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        stream.start_stream()

        print("Listening... (speak now)")
        text_out = ""
        silence_count = 0
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res = rec.Result()
                j = json.loads(res)
                text_out = (j.get("text") or "").strip()
                break
            else:
                silence_count += 1
                if silence_count > 30:  # ~ few seconds
                    break

        stream.stop_stream()
        stream.close()
        pa.terminate()
        return text_out
    except Exception:
        return ""

# ---------------- Main Loop ----------------
def main():
    while True:
        try:
            # Input (voice preferred if available)
            if USE_VOICE:
                user_input = listen_once()
                if not user_input:
                    user_input = input("You: ").strip()
                else:
                    print(f"You (voice): {user_input}")
            else:
                user_input = input("You: ").strip()

            if not user_input:
                continue

            low = user_input.lower().strip()
            if low in ("exit", "quit", "bye"):
                bye = respond3(
                    "Goodbye! Have a safe journey.",
                    "अलविदा! आपकी यात्रा शुभ हो।",
                    "Goodbye! Aapki yatra shubh ho.",
                    detect_language(user_input)
                )
                print(f"Chetna: {bye}")
                if USE_TTS:
                    say(bye)
                break

            if low in ("help", "menu"):
                lang = detect_language(user_input)
                if lang == "hi":
                    help_text = (
                        "मैं आपकी इन बातों में मदद कर सकती हूँ:\n"
                        "- किराया: '701 का किराया' \n"
                        "- समय: '1001 कब निकलती है'\n"
                        "- ट्रैक: '702 कहाँ है'\n"
                        "- रूट: 'दिल्ली से करनाल की बसें'\n"
                        "- अगली बस: 'दिल्ली से करनाल अगली बस'\n"
                        "- स्टेटस: '1001 लेट है?'\n"
                        "- शिकायत: 'complaint bus 702 driver rude'\n"
                        "- सिर्फ नंबर टाइप करें जैसे '702' — उसके डिटेल्स मिलेंगे।\n"
                        "- 'exit' टाइप करके बाहर निकलें।"
                    )
                elif lang == "hi-latn":
                    help_text = (
                        "Main in cheezon me madad kar sakti hoon:\n"
                        "- Kiraya: '701 ka kiraya'\n"
                        "- Samay: '1001 kab nikalti hai'\n"
                        "- Track: '702 kidhar hai'\n"
                        "- Route: 'Delhi se Karnal ki basen'\n"
                        "- Agla bus: 'Delhi se Karnal agla bus'\n"
                        "- Status: '1001 late hai?'\n"
                        "- Sirf number type kare jaise '702' — details milengi.\n"
                        "- 'exit' type karke bahar nikle."
                    )
                else:
                    help_text = (
                        "I can help with:\n"
                        "- Fare: 'fare of bus 701'\n"
                        "- Timing: 'timing of 1001'\n"
                        "- Track: 'where is 702'\n"
                        "- Routes: 'buses from Delhi to Karnal'\n"
                        "- Next bus: 'next bus from Delhi to Karnal'\n"
                        "- Status: 'is 1001 on time?'\n"
                        "- Complaint: 'complaint bus 702 driver rude'\n"
                        "- Type only a number like '702' to see its details.\n"
                        "- Type 'exit' to quit."
                    )
                print(f"Chetna:\n{help_text}")
                continue

            reply, speak_txt = handle_intent(user_input)

            # Log chat
            log_chat(user_input, reply)

            # Output
            print(f"Chetna: {reply}")
            if USE_TTS:
                say(speak_txt)

        except KeyboardInterrupt:
            print("\nChetna: Goodbye!")
            break
        except Exception as e:
            log_event(f"ERROR: {repr(e)}")
            print("Chetna: Something went wrong. Please try again.")

if __name__ == "__main__":
    main()
