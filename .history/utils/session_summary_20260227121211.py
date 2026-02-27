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
        total = len(emotions)
        unique = set(emotions)

        dominant = max(set(emotions), key=emotions.count)

        emotion_reflection = {
            "sadness": "You carried a noticeable sense of heaviness.",
            "anger": "There was clear frustration present.",
            "fear": "There seemed to be underlying worry.",
            "joy": "There were moments of warmth and positivity.",
            "love": "There was emotional depth in what you shared.",
            "neutral": "You explored your thoughts thoughtfully."
        }

        base_line = emotion_reflection.get(dominant, "You expressed meaningful emotions.")

        variation_line = ""

        if len(unique) > 2:
            variation_line = " Your emotions shifted through different states, showing emotional complexity."
        elif len(unique) == 1:
            variation_line = " The feeling remained consistent throughout this session."

        closing_line = " Thank you for allowing yourself to express this."

        return base_line + variation_line + closing_line