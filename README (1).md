# 🚍 Chetna Trackila Bot

Chetna is an AI-powered **bus inquiry chatbot** that helps users check
bus fares, timings, routes, and live locations. It also supports lodging
complaints about buses in multiple languages (English, Hindi, Hinglish).

------------------------------------------------------------------------

## 📂 Project Structure

    CHATBOT CHETNA/
    │── botchetna.py           # Main chatbot runner (entry point)
    │── chetnaintent.py        # Intent detection & entity extraction
    │── chetna_loader.py       # Loads bus data (CSV/JSON) and complaint logs
    │── chetnautils.py         # Language detection & helper utilities
    │
    ├── data/                  # Dataset files
    │   ├── chetnasample_buses.csv   # Raw bus dataset (CSV)
    │   ├── chetnasample_buses.json  # Bus dataset (JSON version for chatbot)
    │
    ├── logs/                  # Logs (auto-generated complaints, activity)
    │
    └── __pycache__/           # Auto-generated cache files

------------------------------------------------------------------------

## ⚙️ Installation

1.  Clone or download the project:

    ``` bash
    git clone https://github.com/yourusername/chatbot-chetna.git
    cd chatbot-chetna
    ```

2.  (Optional) Create a virtual environment:

    ``` bash
    python -m venv venv
    source venv/bin/activate   # Mac/Linux
    venv\Scripts\activate      # Windows
    ```

3.  Install dependencies (if any):

    ``` bash
    pip install -r requirements.txt
    ```

------------------------------------------------------------------------

## ▶️ Usage

Run the chatbot:

``` bash
python botchetna.py
```

Example interaction:

    Chetna started! Type 'help' for options and 'exit' to quit.

    You: Hi  
    Chetna: Hello! I am Chetna. How can I help you with buses today?  

    You: What is the fare of bus 702?  
    Chetna: The fare for bus 702 is ₹220.  

    You: Where is bus 702 now?  
    Chetna: Bus 702 is currently near Ambala.  

    You: Bus 702 driver is very rude.  
    Chetna: Your complaint has been logged. Ticket ID: C-8510.  

------------------------------------------------------------------------

## 📌 Features

-   ✅ Multi-language support (English, Hindi, Hinglish)\
-   ✅ Bus fare inquiry\
-   ✅ Bus timings & schedules\
-   ✅ Live bus tracking (sample data)\
-   ✅ Route search (e.g., *Agra to Lucknow*)\
-   ✅ Complaint lodging with auto Ticket IDs

------------------------------------------------------------------------

## 🛠 How Data is Loaded

-   **`chetnasample_buses.csv`** → Source bus dataset\
-   **`chetnasample_buses.json`** → Converted JSON used by chatbot\
-   **`chetna_loader.py`** → Handles loading these datasets and
    complaint logs

Example (inside `chetna_loader.py`):

``` python
from chetna_loader import load_buses, save_complaint_json

buses = load_buses()  # loads data/chetnasample_buses.json
ticket_id = save_complaint_json("702", "Driver was rude")
```

------------------------------------------------------------------------
