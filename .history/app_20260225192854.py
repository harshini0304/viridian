from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from database.mongo_handler import MongoHandler
from config import Config
from models.text_emotion_model import TextEmotionDetector

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

# ---------------- LOAD EMOTION MODEL ----------------

print("🧠 Loading emotion detector...")
emotion_detector = TextEmotionDetector()
print("✅ Emotion detector ready")

# ---------------- TTS ----------------

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
whisper_model = whisper.load_model("base")
print("✅ Whisper loaded")

# ---------------- THERAPIST RESPONSE ENGINE ----------------

def generate_therapist_reply(emotion, user_text):

    responses = {
        "anger": "It sounds like something really frustrated you. What happened?",
        "sadness": "I'm really sorry you're feeling this way. Do you want to talk about what's weighing on you?",
        "fear": "That sounds overwhelming. What's making you feel anxious right now?",
        "joy": "That’s wonderful to hear. What’s been going well for you?",
        "love": "That sounds meaningful. Tell me more about that connection.",
        "neutral": "I hear you. Tell me more about that."
    }

    return responses.get(emotion, "I’m here with you. Tell me more.")

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

        # 🔥 EMOTION DETECTION
        emotion = emotion_detector.predict_emotion(text)

        # Store emotion in DB
        mongo.add_message(session_id, f"[Detected emotion: {emotion}]", "system")

        # Generate therapist-style reply
        reply = generate_therapist_reply(emotion, text)

        mongo.add_message(session_id, reply, "bot")

        speak_text(reply)

        return jsonify({
            "reply": reply,
            "emotion": emotion
        })

    except Exception as e:
        print("ERROR /send_text:", e)
        return jsonify({"error": "Internal server error"}), 500

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

        # 🔥 EMOTION DETECTION
        emotion = emotion_detector.predict_emotion(transcribed_text)

        mongo.add_message(session_id, f"[Detected emotion: {emotion}]", "system")

        reply = generate_therapist_reply(emotion, transcribed_text)

        mongo.add_message(session_id, reply, "bot")

        speak_text(reply)

        return jsonify({
            "text": transcribed_text,
            "reply": reply,
            "emotion": emotion
        })

    except Exception as e:
        print("ERROR /upload_audio:", e)
        return jsonify({"error": "Audio processing failed"}), 500

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)