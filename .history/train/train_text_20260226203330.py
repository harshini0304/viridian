import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    accuracy_score,
    precision_recall_fscore_support
)
from models.text_emotion_model import TextEmotionDetector
import os
from sklearn.utils.class_weight import compute_class_weight

# ---------------- LOAD DATASETS ----------------

print("📂 Loading GoEmotions CSV files...")

g1 = pd.read_csv("datasets/goemotions_1.csv")
g2 = pd.read_csv("datasets/goemotions_2.csv")
g3 = pd.read_csv("datasets/goemotions_3.csv")

goemo = pd.concat([g1, g2, g3], ignore_index=True)

GOEMOTION_COLUMNS = [
    "anger", "joy", "sadness", "fear", "love", "neutral"
]

def extract_goemotion(row):
    for emo in GOEMOTION_COLUMNS:
        if emo in row and row[emo] == 1:
            return emo
    return "neutral"

print("📂 Loading EmoBank dataset...")
emobank = pd.read_csv("datasets/emobank.csv")

print("🔄 Processing GoEmotions labels...")
goemo["emotion"] = goemo.apply(extract_goemotion, axis=1)
goemo_final = goemo[["text", "emotion"]]

print("🔄 Processing EmoBank labels...")
if "emotion" not in emobank.columns:
    emobank["emotion"] = "neutral"

emobank_final = emobank[["text", "emotion"]]

# ---------------- COMBINE DATASETS ----------------

data = pd.concat([goemo_final, emobank_final], ignore_index=True)

texts = data["text"].astype(str).tolist()
labels = data["emotion"].astype(str).tolist()

print("Total samples:", len(texts))

# ---------------- LABEL MAPPING ----------------

label_map = {
    "anger": 0,
    "joy": 1,
    "sadness": 2,
    "fear": 3,
    "love": 4,
    "neutral": 5
}

y = np.array([label_map.get(lbl.lower(), 5) for lbl in labels])

print("⚖️ Computing class weights...")

classes = np.unique(y)
class_weights = compute_class_weight(
    class_weight="balanced",
    classes=classes,
    y=y
)

class_weights = dict(zip(classes, class_weights))
print("Class weights:", class_weights)

# ---------------- FEATURE EXTRACTION ----------------

print("🧠 Initializing TextEmotionDetector...")
detector = TextEmotionDetector()

print("🔎 Extracting BERT CLS embeddings...")

X = []
for i, text in enumerate(texts):
    try:
        emb = detector.get_bert_embedding(text)

        # 🔥 USE CLS TOKEN (correct method)
        pooled = emb[:, 0, :][0]   # shape (768,)
        X.append(pooled)

    except Exception:
        X.append(np.zeros(768))

    if i % 500 == 0:
        print(f"Processed {i}/{len(texts)} texts")

X = np.array(X)
print("Final feature shape:", X.shape)

# ---------------- TRAIN / TEST SPLIT ----------------

print("🔀 Splitting dataset...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ❌ DO NOT reshape anymore
# Dense model expects (batch, 768)

# ---------------- TRAIN MODEL ----------------

print("🚀 Training Dense Emotion Classifier...")

classifier = detector.classifier

classifier.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=3e-4),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

history = classifier.fit(
    X_train,
    y_train,
    epochs=20,                 # increased training
    batch_size=32,
    class_weight=class_weights,
    validation_data=(X_test, y_test)
)

# ---------------- EVALUATION ----------------

print("📊 Evaluating model...")

y_prob = classifier.predict(X_test)
y_pred = np.argmax(y_prob, axis=1)

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

accuracy = accuracy_score(y_test, y_pred)
precision, recall, f1, _ = precision_recall_fscore_support(
    y_test, y_pred, average="weighted"
)

metrics = {
    "accuracy": float(accuracy),
    "precision": float(precision),
    "recall": float(recall),
    "f1_score": float(f1),
}

print("\nFinal Metrics:")
for k, v in metrics.items():
    print(f"{k}: {v:.4f}")

# ---------------- SAVE MODEL ----------------

os.makedirs("../saved_models", exist_ok=True)

print("\n💾 Saving trained emotion model...")

classifier.save_weights("../saved_models/text_emotion_hybrid.h5")

print("✅ Model weights saved")
print("🎉 Text Emotion Training Complete.")