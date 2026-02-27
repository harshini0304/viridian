class SessionSummary:

    def __init__(self):
        self.sessions = {}

    def update(self, session_id, text, emotion):
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "messages": [],
                "emotions": []
            }

        self.sessions[session_id]["messages"].append(text)
        self.sessions[session_id]["emotions"].append(emotion)

    def generate_summary(self, session_id):

        data = self.sessions.get(session_id)
        if not data:
            return None

        emotions = data["emotions"]

        dominant = max(set(emotions), key=emotions.count)

        return {
            "dominant_emotion": dominant,
            "message_count": len(data["messages"]),
            "emotional_variation": len(set(emotions))
        }