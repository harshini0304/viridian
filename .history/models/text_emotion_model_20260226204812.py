from transformers import pipeline

class TextEmotionDetector:

    def __init__(self):
        print("🧠 Loading pretrained emotion model...")
        
        self.classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            top_k=None
        )

        print("✅ Emotion model ready")

        # map model labels → your chatbot labels
        self.label_map = {
            "anger": "anger",
            "disgust": "anger",
            "fear": "fear",
            "joy": "joy",
            "sadness": "sadness",
            "love": "love",
            "surprise": "neutral",
            "neutral": "neutral"
        }

    def predict_emotion(self, text):

        results = self.classifier(text)[0]

        # pick highest score
        best = max(results, key=lambda x: x["score"])

        emotion = self.label_map.get(best["label"], "neutral")

        print("Predicted:", emotion, "| confidence:", best["score"])

        return emotion

    def predict_emotion_proba(self, text):

        results = self.classifier(text)[0]

        mapped = {}

        for r in results:
            label = self.label_map.get(r["label"], "neutral")
            mapped[label] = float(r["score"])

        return mapped