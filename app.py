from flask import Flask, request, jsonify, send_file
import requests
import os
import tempfile

app = Flask(__name__)

GROQ_KEY = os.getenv("GROQ_KEY")

# -----------------------------------------------
# STEP 1: Audio → Text (Whisper on Groq)
# -----------------------------------------------
def speech_to_text(audio_bytes):
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
    data = {"model": "whisper-large-v3", "language": "sk"}
    r = requests.post(url, headers=headers, files=files, data=data)
    return r.json().get("text", "")

# -----------------------------------------------
# STEP 2: Text → AI Answer (Groq llama3)
# -----------------------------------------------
def ask_ai(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful voice assistant. Answer in the same language the user speaks. Keep answers short and clear — maximum 2-3 sentences."
            },
            {"role": "user", "content": text}
        ]
    }
    r = requests.post(url, json=data, headers=headers)
    return r.json()["choices"][0]["message"]["content"]

# -----------------------------------------------
# STEP 3: Text → Voice (TTS on Groq)
# -----------------------------------------------
def text_to_speech(text):
    url = "https://api.groq.com/openai/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "playai-tts",
        "input": text,
        "voice": "Fritz-PlayAI",
        "response_format": "wav"
    }
    r = requests.post(url, json=data, headers=headers)
    return r.content

# -----------------------------------------------
# MAIN ENDPOINT — ESP32 sends audio, gets audio back
# -----------------------------------------------
@app.route("/talk", methods=["POST"])
def talk():
    try:
        audio_bytes = request.data

        # 1. Audio → text
        question = speech_to_text(audio_bytes)
        print(f"User said: {question}")

        if not question:
            return jsonify({"error": "Could not understand audio"}), 400

        # 2. Text → AI answer
        answer = ask_ai(question)
        print(f"AI answer: {answer}")

        # 3. Answer → voice audio
        audio_response = text_to_speech(answer)

        # 4. Send audio back to ESP32
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp.write(audio_response)
        tmp.close()

        return send_file(tmp.name, mimetype="audio/wav")

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "ESP32 AI Robot server is running!"

if _name_ == "__main__":
    app.run(host="0.0.0.0", port=10000)
