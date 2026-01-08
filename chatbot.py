import tkinter as tk
from datetime import datetime
import threading
import time
import google.generativeai as genai
import pyttsx3  # For text-to-speech

# ===== CONFIGURATION =====
API_KEY = " Paste your Gemini API key here"  
MODEL_NAME = "gemini-1.5-flash"

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

# Text-to-speech setup
tts = pyttsx3.init()
tts.setProperty("rate", 170)  # Speed
tts.setProperty("voice", tts.getProperty("voices")[1].id)  # Female voice

# Chat history for context
chat_history = []

# ===== SEND MESSAGE =====
def send_message(event=None):
    user_input = entry.get()
    if not user_input.strip():
        return
    entry.delete(0, tk.END)

    insert_message(user_input, "user")

    chat_history.append({"role": "user", "parts": [user_input]})

    # Start bot reply in a new thread
    threading.Thread(target=bot_reply).start()

# ===== BOT REPLY WITH TYPING ANIMATION =====
def bot_reply():
    insert_typing_indicator()

    time.sleep(0.8)  # Short pause before fetching response
    try:
        response = model.generate_content(chat_history)
        reply = response.text
    except Exception as e:
        reply = f"Error: {str(e)}"

    remove_typing_indicator()
    insert_message(reply, "bot")

    chat_history.append({"role": "model", "parts": [reply]})

    # Voice output
    threading.Thread(target=speak, args=(reply,)).start()

# ===== TEXT-TO-SPEECH =====
def speak(text):
    tts.say(text)
    tts.runAndWait()

# ===== INSERT MESSAGE BUBBLE =====
def insert_message(message, sender):
    time_now = datetime.now().strftime("%H:%M")
    if sender == "user":
        bubble_color = "#4CAF50"
        text_color = "white"
        align = "e"
    else:
        bubble_color = "#2C3E50"
        text_color = "white"
        align = "w"

    bubble_frame = tk.Frame(chat_frame, bg="#1E1E1E")
    bubble_frame.pack(anchor=align, pady=2, padx=10)

    bubble = tk.Label(
        bubble_frame,
        text=f"{message}\n({time_now})",
        bg=bubble_color,
        fg=text_color,
        wraplength=350,
        justify="left",
        font=("Segoe UI", 11),
        padx=10,
        pady=5
    )
    bubble.pack(anchor=align, fill="x", ipadx=5, ipady=5)

    canvas.yview_moveto(1)

# ===== TYPING INDICATOR =====
typing_label = None

def insert_typing_indicator():
    global typing_label
    typing_label = tk.Label(chat_frame, text="Bot is typing...", fg="gray", bg="#1E1E1E", font=("Segoe UI", 10, "italic"))
    typing_label.pack(anchor="w", padx=10, pady=2)
    canvas.yview_moveto(1)

def remove_typing_indicator():
    global typing_label
    if typing_label:
        typing_label.destroy()
        typing_label = None

# ===== GUI SETUP =====
root = tk.Tk()
root.title("AI Chatbot 🤖 (Gemini)")
root.geometry("500x600")
root.config(bg="#1E1E1E")

canvas = tk.Canvas(root, bg="#1E1E1E", highlightthickness=0)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
chat_frame = tk.Frame(canvas, bg="#1E1E1E")

chat_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=chat_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

entry_frame = tk.Frame(root, bg="#1E1E1E")
entry_frame.pack(fill="x", pady=5)

entry = tk.Entry(entry_frame, font=("Segoe UI", 12), bg="#2C2C2C", fg="white", insertbackground="white")
entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
entry.bind("<Return>", send_message)

send_btn = tk.Button(entry_frame, text="Send", command=send_message, font=("Segoe UI", 11), bg="#4CAF50", fg="white")
send_btn.pack(side="right", padx=5, pady=5)

root.mainloop()

