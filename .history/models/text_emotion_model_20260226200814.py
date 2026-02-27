import torch
import numpy as np
import tensorflow as tf
from transformers import BertTokenizer, BertModel
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


# ===============================
# SIMPLE DENSE EMOTION CLASSIFIER
# ===============================

class EmotionClassifier(tf.keras.Model):

    def __init__(self, num_classes=6):
        super(EmotionClassifier, self).__init__()

        self.dense1 = tf.keras.layers.Dense(256, activation="relu")
        self.dropout = tf.keras.layers.Dropout(0.3)
        self.out = tf.keras.layers.Dense(num_classes, activation="softmax")

    def call(self, inputs):
        x = self.dense1(inputs)
        x = self.dropout(x)
        return self.out(x)


# ===============================
# TEXT EMOTION DETECTOR
# ===============================

class TextEmotionDetector:

    def __init__(self):

        print("🧠 Loading BERT...")
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.bert = BertModel.from_pretrained("bert-base-uncased")

        print("🧠 Building emotion classifier architecture...")

        # Create classifier
        self.classifier = EmotionClassifier()

        # IMPORTANT: Build with correct input shape (768 only)
        dummy_input = np.zeros((1, 768), dtype=np.float32)
        self.classifier(dummy_input)

        # Load trained weights
        self.classifier.load_weights("saved_models/text_emotion_hybrid.h5")

        print("✅ Emotion classifier loaded")
        print("✅ Text emotion model ready")


    # ===============================
    # BERT EMBEDDING
    # ===============================

    def get_bert_embedding(self, text):
        tokens = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=64
        )

        with torch.no_grad():
            outputs = self.bert(**tokens)

        return outputs.last_hidden_state.numpy()


    # ===============================
    # PREDICT EMOTION
    # ===============================

    def predict_emotion(self, text):

        emb = self.get_bert_embedding(text)

        # 🔥 CLS TOKEN (best representation)
        pooled = emb[:, 0, :][0]      # shape (768,)
        pooled = pooled.reshape(1, 768)

        pred = self.classifier.predict(pooled)

        confidence = np.max(pred)
        emotion_index = np.argmax(pred)

        labels = ["anger", "joy", "sadness", "fear", "love", "neutral"]

        # Confidence safeguard
        if confidence < 0.35:
            final_emotion = "neutral"
        else:
            final_emotion = labels[emotion_index]

        print("Prediction raw:", pred)
        print("Confidence:", confidence)
        print("Pred label:", final_emotion)

        return final_emotion


    # ===============================
    # EMOTION PROBABILITIES
    # ===============================

    def predict_emotion_proba(self, text):

        emb = self.get_bert_embedding(text)

        pooled = emb[:, 0, :][0]
        pooled = pooled.reshape(1, 768)

        probs = self.classifier.predict(pooled)[0]

        emotion_map = {
            0: "anger",
            1: "joy",
            2: "sadness",
            3: "fear",
            4: "love",
            5: "neutral"
        }

        return {
            emotion_map[i]: float(probs[i])
            for i in range(len(probs))
        }


    # ===============================
    # EVALUATION
    # ===============================

    def evaluate(self, y_true, y_pred):

        acc = accuracy_score(y_true, y_pred)

        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true,
            y_pred,
            average='weighted'
        )

        return {
            "accuracy": float(acc),
            "precision": float(precision),
            "f1_score": float(f1)
        }