from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from config import Config
from models.text_emotion_model import TextEmotionDetector
from utils.therapy_engine import TherapyEngine
from utils.session_summary import SessionSummary

import pyttsx3
import os
import uuid
import whisper
import threading

# ---------------- APP INIT ----------------

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

chat_memory = {}

# ---------------- LOAD MODELS ----------------

print("🧠 Loading emotion detector...")
emotion_detector = TextEmotionDetector()
print("✅ Emotion detector ready")

therapy_engine = TherapyEngine()
summary_engine = SessionSummary()

# ---------------- TTS ----------------

engine = pyttsx3.init()
engine.setProperty('rate', 170)
tts_lock = threading.Lock()

def speak_text(text):
    def run():
        with tts_lock:
            try:
                engine.stop()
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print("TTS error:", e)

    threading.Thread(target=run, daemon=True).start()

# ---------------- WHISPER ----------------

print("🧠 Loading Whisper model...")
whisper_model = whisper.load_model("base")
print("✅ Whisper loaded")

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/start_session", methods=["POST"])
def start_session():
    session_id = str(uuid.uuid4())
    chat_memory[session_id] = []
    return jsonify({"session_id": session_id})

# ---------------- TEXT INPUT ----------------

@app.route("/send_text", methods=["POST"])
def send_text():
    try:
        data = request.json
        session_id = data["session_id"]
        text = data["text"]

        # Save user message
        chat_memory[session_id].append({
            "sender": "user",
            "text": text
        })

        # Emotion detection
        emotion = emotion_detector.predict_emotion(text)

        # Update summary engine
        summary_engine.update(session_id, text, emotion)

        # Save emotion log
        chat_memory[session_id].append({
            "sender": "system",
            "text": f"[Detected emotion: {emotion}]"
        })

        # Update therapy engine
        therapy_engine.update_emotional_state(session_id, emotion)

        reply = therapy_engine.build_reply(
            session_id,
            emotion
        )

        # Save bot reply
        chat_memory[session_id].append({
            "sender": "bot",
            "text": reply
        })

        return jsonify({
            "reply": reply,
            "emotion": emotion
        })

    except Exception as e:
        print("ERROR /send_text:", e)
        return jsonify({"error": "Internal server error"}), 500

# ---------------- AUDIO INPUT ----------------

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

        chat_memory[session_id].append({
            "sender": "user",
            "text": transcribed_text
        })

        emotion = emotion_detector.predict_emotion(transcribed_text)

        summary_engine.update(session_id, transcribed_text, emotion)

        chat_memory[session_id].append({
            "sender": "system",
            "text": f"[Detected emotion: {emotion}]"
        })

        therapy_engine.update_emotional_state(session_id, emotion)

        reply = therapy_engine.build_reply(session_id, emotion)

        chat_memory[session_id].append({
            "sender": "bot",
            "text": reply
        })

        speak_text(reply)

        return jsonify({
            "reply": reply,
            "emotion": emotion
        })

    except Exception as e:
        print("ERROR /upload_audio:", e)
        return jsonify({"error": "Audio processing failed"}), 500
    


@app.route("/end_session", methods=["POST"])
def end_session():
    try:
        data = request.json
        session_id = data["session_id"]

        summary = summary_engine.generate_summary(session_id)

        if not summary:
            return jsonify({"summary": None})

        summary_text = (
            f"🧠 Session Summary:\n\n"
            f"• Dominant emotion: {summary['dominant_emotion']}\n"
            f"• Messages shared: {summary['message_count']}\n"
            f"• Emotional range: {summary['emotional_variation']} different emotions\n\n"
            f"You showed courage by expressing this."
        )

        return jsonify({"summary": summary_text})

    except Exception as e:
        print("ERROR /end_session:", e)
        return jsonify({"error": "Failed to generate summary"}), 500

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)