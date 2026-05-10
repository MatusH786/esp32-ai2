from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

GROQ_KEY = os.getenv("GROQ_KEY")

def ask_ai(text):

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "user", "content": text}
        ]
    }

    r = requests.post(url, json=data, headers=headers)

    try:
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "Chyba AI odpovede"

@app.route("/ask", methods=["POST"])
def ask():

    user_text = request.json["text"]

    answer = ask_ai(user_text)

    return jsonify({"text": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
