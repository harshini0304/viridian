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

        emotion_lines = {
            "sadness": [
                "That sounds heavy to carry.",
                "There’s a lot weighing on you emotionally.",
                "It feels like this has been draining you.",
                "That kind of feeling can stay quietly for a long time."
            ],
            "anger": [
                "That sounds frustrating.",
                "There’s a lot of tension in this.",
                "Something here feels deeply upsetting."
            ],
            "fear": [
                "That sounds overwhelming.",
                "That uncertainty can feel intense.",
                "It makes sense your mind is trying to protect you."
            ],
            "joy": [
                "That sounds meaningful.",
                "There’s warmth in what you're sharing.",
                "Moments like that stay with people."
            ],
            "love": [
                "That connection seems important.",
                "There’s emotional depth here.",
                "That kind of bond shapes us."
            ],
            "neutral": [
                "I'm here with you.",
                "Take your time.",
                "You can share at your own pace."
            ]
        }

        base = random.choice(emotion_lines.get(emotion, emotion_lines["neutral"]))

        # pattern intelligence
        if pattern == "persistent_sadness":
            return base + " It seems this feeling has been staying with you for some time."

        if pattern == "anxiety_pattern":
            return base + " There seems to be a recurring sense of worry here."

        if pattern == "emotional_distress":
            return base + " You've been carrying intense emotions repeatedly."

        return base

    def build_reply(self, session_id, emotion):

        pattern = self.detect_pattern(session_id)
        intensity = self.emotion_intensity(session_id)

        psychological_line = self.generate_psychological_response(
            emotion,
            pattern
        )

        if random.random() < 0.25:
          return psychological_line
        
        short_support = [
            "I'm here.",
            "I understand.",
            "Go on."
        ]

        medium_questions = [
            "What’s been affecting you most?",
            "When did this begin feeling stronger?",
            "What do you think is behind this?"
        ]

        deep_questions = [
            "What part of this feels hardest to carry?",
            "Does this connect to something deeper happening in your life?",
            "What thoughts usually come when this feeling appears?"
        ]

        if intensity == "low":
            return f"{psychological_line} {random.choice(short_support)}"

        if intensity == "medium":
            return f"{psychological_line} {random.choice(medium_questions)}"

        if intensity == "high":
            return f"{psychological_line} {random.choice(deep_questions)}"
    
    def emotion_intensity(self, session_id):
        emotions = self.user_state.get(session_id, [])

        if len(emotions) < 3:
            return "low"

        if emotions.count(emotions[-1]) >= 3:
            return "high"

        return "medium"
    
    def detect_emotional_progression(self, session_id):

        messages = self.get_recent_user_messages(session_id, limit=6)

        sadness_count = 0
        intensity_score = 0

        for msg in messages:
            text = msg.lower()

            if "low" in text or "sad" in text or "tired" in text:
                sadness_count += 1

            if "very" in text or "always" in text or "everyday" in text:
                intensity_score += 1

            if "can't" in text or "nothing helps" in text:
                intensity_score += 2

        if sadness_count >= 4:
            return "persistent_low"

        if intensity_score >= 3:
            return "emotional_risk"

        return None