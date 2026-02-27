import random

class TherapyEngine:

    def __init__(self):
        self.user_state = {}

    def update_emotional_state(self, session_id, emotion):
        if session_id not in self.user_state:
            self.user_state[session_id] = []

        self.user_state[session_id].append(emotion)

        # keep last 10 emotions
        self.user_state[session_id] = self.user_state[session_id][-10:]

    def detect_pattern(self, session_id):
        emotions = self.user_state.get(session_id, [])

        if emotions.count("sadness") >= 4:
            return "persistent_sadness"

        if emotions.count("anger") >= 4:
            return "emotional_distress"

        if emotions.count("fear") >= 4:
            return "anxiety_pattern"

        return None

    def generate_psychological_response(self, emotion, pattern):

        if pattern == "persistent_sadness":
            return "It seems this feeling has been staying with you for some time."

        if pattern == "anxiety_pattern":
            return "There seems to be a recurring sense of worry here."

        if pattern == "emotional_distress":
            return "You've been carrying intense emotions repeatedly."

        # emotion-based intelligence
        emotion_logic = {
            "sadness": "That sounds heavy to carry.",
            "anger": "That sounds frustrating.",
            "fear": "That sounds overwhelming.",
            "joy": "That sounds meaningful.",
            "love": "That connection seems important.",
            "neutral": "I'm here with you."
        }

        return emotion_logic.get(emotion, "I'm listening.")

    def build_reply(self, session_id, emotion):

        pattern = self.detect_pattern(session_id)

        psychological_line = self.generate_psychological_response(
            emotion,
            pattern
        )

        question_bank = [
            "What has been affecting you the most?",
            "When did this start feeling stronger?",
            "What do you think is behind this feeling?",
            "Would you like to talk more about it?"
        ]

        support_bank = [
            "You're not alone in this.",
            "I'm here to listen.",
            "We can work through this step by step."
        ]

        return f"{psychological_line} {random.choice(question_bank)} {random.choice(support_bank)}"