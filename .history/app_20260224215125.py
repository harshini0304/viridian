from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from database.mongo_handler import MongoHandler
from config import Config
import pyttsx3
import os
import uuid
import whisper
import threading

# ---------------- APP INIT ----------------

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

mongo = MongoHandler()

# ---------------- TTS (SAFE, NON-BLOCKING) ----------------

engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak_text(text):
    def run():
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print("TTS error:", e)

    threading.Thread(target=run, daemon=True).start()

# ---------------- WHISPER ----------------

print("🧠 Loading Whisper model...")
whisper_model = whisper.load_model("base")  # base = best balance for CPU
print("✅ Whisper loaded")

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/start_session", methods=["POST"])
def start_session():
    data = request.json
    username = data.get("username", "anonymous")
    session_id = mongo.create_session(username)
    return jsonify({"session_id": session_id})

@app.route("/send_text", methods=["POST"])
def send_text():
    try:
        data = request.json
        session_id = data["session_id"]
        text = data["text"]

        mongo.add_message(session_id, text, "user")

        reply = "I hear you. Tell me more about that."
        mongo.add_message(session_id, reply, "bot")

        speak_text(reply)

        return jsonify({"reply": reply})

    except Exception as e:
        print("ERROR /send_text:", e)
        return jsonify({"error": "Internal server error"}), 500

# ---------------- AUDIO (REAL STT) ----------------

@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    try:
        audio = request.files["audio"]
        session_id = request.form["session_id"]

        os.makedirs("temp_audio", exist_ok=True)
        filename = f"{uuid.uuid4()}.webm"
        path = os.path.join("temp_audio", filename)
        audio.save(path)

        print("🎙 Transcribing audio with Whisper...")
        result = whisper_model.transcribe(path)
        transcribed_text = result["text"].strip()

        if not transcribed_text:
            transcribed_text = "[Could not understand audio]"

        mongo.add_message(session_id, transcribed_text, "user")

        reply = "Thank you for sharing that. How did it make you feel?"
        mongo.add_message(session_id, reply, "bot")

        speak_text(reply)

        return jsonify({
            "text": transcribed_text,
            "reply": reply
        })

    except Exception as e:
        print("ERROR /upload_audio:", e)
        return jsonify({"error": "Audio processing failed"}), 500

# ---------------- RUN (NO AUTO-RELOADER) ----------------

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
