from flask import Flask, request, jsonify, send_file
import requests
import os
import tempfile

app = Flask(_name_)

GROQ_KEY = os.getenv("GROQ_KEY")

def speech_to_text(audio_bytes):
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
    data = {"model": "whisper-large-v3", "language": "sk"}
    r = requests.post(url, headers=headers, files=files, data=data)
    return r.json().get("text", "")

def ask_ai(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3
Poslané
Vytvoriť
Napísať používateľovi
