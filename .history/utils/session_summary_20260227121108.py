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