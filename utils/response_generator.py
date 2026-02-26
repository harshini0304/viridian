import random

# =============================
# EMOTIONAL ACKNOWLEDGEMENT
# =============================

ACKNOWLEDGEMENTS = {
    "sadness": [
        "I'm really sorry you're feeling this way.",
        "That sounds emotionally heavy.",
        "It seems like this has been weighing on you."
    ],
    "anger": [
        "That sounds really frustrating.",
        "I can sense a lot of tension there.",
        "That would make anyone feel upset."
    ],
    "fear": [
        "That sounds really overwhelming.",
        "I understand why that would worry you.",
        "That kind of uncertainty can feel intense."
    ],
    "joy": [
        "That sounds really positive.",
        "I'm glad something is going well for you.",
        "That must feel uplifting."
    ],
    "love": [
        "That sounds meaningful.",
        "That connection seems important to you.",
        "Moments like that can feel special."
    ],
    "neutral": [
        "I'm here with you.",
        "I'm listening.",
        "Tell me more."
    ]
}

# =============================
# REFLECTION ENGINE
# (NOT repeating user words)
# =============================

REFLECTIONS = [
    "It sounds like this has been on your mind a lot lately.",
    "This situation seems to be affecting you deeply.",
    "You're carrying a lot internally.",
    "That must take a lot of emotional energy."
]

# =============================
# THERAPIST QUESTIONS
# =============================

QUESTIONS = [
    "What has been the hardest part of this for you?",
    "When did this start feeling this intense?",
    "What do you think is contributing most to this feeling?",
    "Would you like to talk more about what’s behind this?"
]

# =============================
# SUPPORTIVE LINES
# =============================

SUPPORT_LINES = [
    "You're not alone in this.",
    "I'm here to listen.",
    "We can work through this step by step.",
    "Your feelings are completely valid."
]

# =============================
# MEMORY ENGINE
# Detect repeating struggles
# =============================

def detect_emotional_theme(previous_messages):

    if not previous_messages:
        return None

    stress_count = 0
    sadness_count = 0
    fear_count = 0

    for msg in previous_messages:
        if msg["sender"] == "user":
            text = msg["text"].lower()

            if "stress" in text or "pressure" in text:
                stress_count += 1

            if "sad" in text or "hurt" in text:
                sadness_count += 1

            if "afraid" in text or "fail" in text or "anxious" in text:
                fear_count += 1

    if stress_count >= 2:
        return "stress"
    if sadness_count >= 2:
        return "sadness"
    if fear_count >= 2:
        return "fear"

    return None


# =============================
# MAIN THERAPIST REPLY ENGINE
# =============================

def generate_therapist_reply(emotion, user_text, previous_messages=None):

    ack = random.choice(ACKNOWLEDGEMENTS.get(emotion, ACKNOWLEDGEMENTS["neutral"]))

    reflect = random.choice(REFLECTIONS)
    question = random.choice(QUESTIONS)
    support = random.choice(SUPPORT_LINES)

    # 🔥 memory awareness
    theme = detect_emotional_theme(previous_messages)

    memory_line = ""
    if theme == "stress":
        memory_line = "You've been under pressure for a while now."
    elif theme == "sadness":
        memory_line = "It seems this sadness has been staying with you."
    elif theme == "fear":
        memory_line = "There seems to be a growing sense of worry here."

    # FINAL RESPONSE BUILD
    if memory_line:
        return f"{ack} {memory_line} {reflect} {question} {support}"

    return f"{ack} {reflect} {question} {support}"