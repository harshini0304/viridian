import torch
import numpy as np
import tensorflow as tf
from transformers import BertTokenizer, BertModel
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

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
        config.update({
            "num_classes": self.num_classes
        })
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)

class TextEmotionDetector:

    def __init__(self):

        print("🧠 Loading BERT...")
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.bert = BertModel.from_pretrained("bert-base-uncased")

        print("🧠 Loading trained emotion classifier...")

        print("🧠 Loading trained emotion classifier...")

# 1️⃣ Create architecture
        self.classifier = BERT_CNN_LSTM()

# 2️⃣ Build model (VERY IMPORTANT)
        self.classifier.build(input_shape=(None, 768, 1))

# 3️⃣ Load weights
        self.classifier.load_weights("saved_models/text_emotion_hybrid.keras")

        print("✅ Emotion classifier loaded")

        print("✅ Text emotion model ready")

    def get_bert_embedding(self, text):
        tokens = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)

        with torch.no_grad():
            outputs = self.bert(**tokens)

        return outputs.last_hidden_state.numpy()

    def predict_emotion(self, text):
        emb = self.get_bert_embedding(text)

        pooled = np.mean(emb, axis=1)[0]
        pooled = pooled.reshape(1, 768, 1)

        pred = self.classifier.predict(pooled)

        emotion = np.argmax(pred, axis=1)

        labels = ["anger","joy","sadness","fear","love","neutral"]

        return labels[int(emotion[0])]
    
    def predict_emotion_proba(self, text):
        emb = self.get_bert_embedding(text)
     
        pooled = np.mean(emb, axis=1)[0]
        pooled = pooled.reshape(1, 768, 1)

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
     
     
    def evaluate(self, y_true, y_pred):
        acc = accuracy_score(y_true, y_pred)

        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted')

        return {
            "accuracy": float(acc),
            "precision": float(precision),
            "f1_score": float(f1)
        }
