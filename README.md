# 📌 Chetna Trackila Bot

**Chetna Trackila** is a simple **bus inquiry chatbot** built with Python.  
It helps users with common queries like:  

- Bus timings and schedules  
- Tracking current bus location  
- Fare information  
- Route details between two cities  
- Complaints about buses/drivers  
- Greetings & small talk  
⚡ This chatbot combines rule-based intent and entity extraction with an open-source LLM (Large Language Model) as a fallback to handle queries outside predefined patterns.

The bot uses **intent detection + rule-based entity extraction** to understand queries in **English, Hindi, and Hinglish**.  

---

## 🚀 Features
Greetings support

Fare inquiry

Timing / schedule inquiry

Bus tracking (location)

Bus status inquiry

Complaints system with Ticket ID

Route information (between cities)

Time period detection (morning/afternoon/evening/night)

Next bus inquiry

Language detection (English, Hindi, Hinglish)

LLM fallback (local GPT4All)

Robust entity extraction (bus number, source, destination)

Optional voice input (Vosk)

Optional text-to-speech (pyttsx3)

## 📂 Project Structure

```
CHATBOT CHETNA/
│
├── data/
│   ├── chetnasample_buses.csv     # Bus data (source, destination, timings, fare, etc.)
│   ├── chetnasample_buses.json    # JSON representation of bus data
│
├── logs/                          # Complaint logs, runtime logs
│─── models
│   ├── ggml-gpt4all-j-v1.3-groovy.bin
│ 
├── botchetna.py                   # Main chatbot runner
├── chetna_loader.py               # Loads bus data from CSV/JSON
├── chetnaintent.py                # Handles intent + entity extraction
├── chetnautils.py                 # Utilities (language detection, helpers)
└── README.md                      # Project documentation
```

---

## ⚙️ Installation & Setup (Step by Step in VS Code)

Follow these steps carefully to set up the chatbot in **Visual Studio Code**:

### 1. Install Python
- Download and install **Python 3.10+** from [python.org](https://www.python.org/downloads/).  
- During installation, check the box **"Add Python to PATH"**.  
- Verify installation:  
  - Open **Command Prompt** and run:  
    ```powershell
    python --version
    ```

### 2. Install Visual Studio Code
- Download **VS Code** from [code.visualstudio.com](https://code.visualstudio.com/).  
- Install the following extensions in VS Code:  
  - **Python (Microsoft)**  
  - **Pylance**  
  - **Code Runner** (optional, for running Python scripts easily)  

### 3. Open the Project in VS Code
- Open VS Code.  
- Go to **File → Open Folder → Select `CHATBOT CHETNA/`**.  

### 4. Set Up Virtual Environment (Recommended)
- Open VS Code terminal (`Ctrl + ~`).  
- Run the following commands:  
  ```powershell
  python -m venv venv
  ```  
- Activate the virtual environment:  
  ```powershell
  venv\Scriptsactivate
  ```  

### 5. Install Required Packages
- Install dependencies inside the activated environment:  
  ```powershell
  pip install langdetect
  pip install pandas
  ```

*(If you want, create a `requirements.txt` with these two lines:)*  
```
langdetect
pandas
```
and then run:  
```powershell
pip install -r requirements.txt
```

### 6. Run the Chatbot
- In VS Code terminal, run:  
  ```powershell
  python botchetna.py
  ```

- The bot will start:  
  ```
  Chetna started! Type 'help' for options and 'exit' to quit.
  ```

---

## 💻 Usage

Once the bot starts, you can chat with it in the terminal.

**Examples:**
```
You: hii
Chetna: Hello! I am Chetna. How can I help you with buses today?

You: What is the fare of bus 702?
Chetna: The fare for bus 702 is ₹220.

You: Where is bus 1001 now?
Chetna: Bus 1001 is currently near Ambala.

You: Agra se Lucknow ke buses
Chetna: Bus 702 Agra se Lucknow ke liye 11:45 AM baje, kiraya ₹220.

You: Bus 702 driver is very rude
Chetna: Your complaint has been logged. Ticket ID: C-4567.
```

---

## 👨‍💻 Author

Developed with by Team 8 : Pragya Singh , Jatin Yadav ,Dendi Priyanka Reddy 
