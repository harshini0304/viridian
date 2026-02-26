import random

# Emotion-specific acknowledgement phrases
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
        "That sounds really scary.",
        "I understand why that would worry you.",
        "That kind of uncertainty can feel overwhelming."
    ],
    "joy": [
        "That sounds wonderful!",
        "I'm glad you're feeling this way.",
        "That’s really uplifting to hear."
    ],
    "love": [
        "That sounds meaningful.",
        "That connection seems important to you.",
        "It's beautiful when we feel that way."
    ],
    "neutral": [
        "I’m here with you.",
        "Tell me more about that.",
        "I’m listening."
    ]
}

# Therapist reflection templates
REFLECTIONS = [
    "When you say that, it sounds like {context}.",
    "It seems this situation is affecting you deeply.",
    "That must be difficult to carry."
]

# Gentle therapist questions
QUESTIONS = [
    "What’s been the hardest part of this for you?",
    "When did you first start feeling this way?",
    "What do you think is causing this feeling?",
    "Would you like to talk more about it?"
]

# Supportive closers
SUPPORT_LINES = [
    "You're not alone in this.",
    "I'm here to listen.",
    "We can work through this together.",
    "Your feelings are valid."
]


def generate_therapist_reply(emotion, user_text):

    ack = random.choice(ACKNOWLEDGEMENTS.get(emotion, ACKNOWLEDGEMENTS["neutral"]))

    if "exam" in user_text.lower():
        reflect = "Exams can create a lot of pressure and expectations."
    elif "family" in user_text.lower():
        reflect = "Family situations can be emotionally complex."
    elif "friend" in user_text.lower():
        reflect = "Relationships can affect us deeply."
    else:
        reflect = random.choice(REFLECTIONS)

    question = random.choice(QUESTIONS)
    support = random.choice(SUPPORT_LINES)

    return f"{ack} {reflect} {question} {support}"

   
     