import torch
import numpy as np
import tensorflow as tf
from transformers import BertTokenizer, BertModel
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


# =====================================
# HYBRID MODEL (CNN + LSTM)
# =====================================

class BERT_CNN_LSTM(tf.keras.Model):

    def __init__(self, num_classes=6, **kwargs):
        super(BERT_CNN_LSTM, self).__init__(**kwargs)

        self.num_classes = num_classes

        self.lstm = tf.keras.layers.LSTM(128, return_sequences=True)
        self.conv = tf.keras.layers.Conv1D(64, 3, activation='relu')
        self.pool = tf.keras.layers.GlobalMaxPooling1D()
        self.dense = tf.keras.layers.Dense(64, activation='relu')
        self.out = tf.keras.layers.Dense(num_classes, activation='softmax')

    def call(self, inputs):
        x = self.lstm(inputs)
        x = self.conv(x)
        x = self.pool(x)
        x = self.dense(x)
        return self.out(x)

    def get_config(self):
        config = super(BERT_CNN_LSTM, self).get_config()
        config.update({"num_classes": self.num_classes})
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)


# =====================================
# TEXT EMOTION DETECTOR
# =====================================

class TextEmotionDetector:

    def __init__(self):

        print("🧠 Loading BERT...")
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.bert = BertModel.from_pretrained("bert-base-uncased")

        print("🧠 Building emotion classifier architecture...")

        # Build architecture
        self.classifier = BERT_CNN_LSTM()

        dummy_input = np.zeros((1, 768, 1), dtype=np.float32)
        self.classifier(dummy_input)

        print("🧠 Loading trained emotion classifier weights...")
        self.classifier.load_weights("saved_models/text_emotion_hybrid.h5")

        print("✅ Emotion classifier loaded")
        print("✅ Text emotion model ready")

        # ⭐ FINAL LABEL ORDER — DO NOT CHANGE
        # (matches your trained model)
        self.labels = [
            "sadness",
            "anger",
            "joy",
            "fear",
            "neutral",
            "love"
        ]


    # =====================================
    # BERT EMBEDDING
    # =====================================

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


    # =====================================
    # EMOTION PREDICTION
    # =====================================

    def predict_emotion(self, text):

        emb = self.get_bert_embedding(text)

        pooled = np.mean(emb, axis=1)[0]
        pooled = pooled.reshape(1, 768, 1)

        pred = self.classifier.predict(pooled, verbose=0)[0]

        print("Prediction raw:", pred)

        pred_index = np.argmax(pred)
        confidence = pred[pred_index]

        print("Pred index:", pred_index)
        print("Confidence:", confidence)

        # ⭐ CONFIDENCE FILTER
        if confidence < 0.35:
            return "neutral"

        emotion = self.labels[pred_index]

        print("Pred label:", emotion)

        return emotion


    # =====================================
    # PROBABILITY OUTPUT
    # =====================================

    def predict_emotion_proba(self, text):

        emb = self.get_bert_embedding(text)

        pooled = np.mean(emb, axis=1)[0]
        pooled = pooled.reshape(1, 768, 1)

        probs = self.classifier.predict(pooled, verbose=0)[0]

        return {
            self.labels[i]: float(probs[i])
            for i in range(len(probs))
        }


    # =====================================
    # MODEL EVALUATION
    # =====================================

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