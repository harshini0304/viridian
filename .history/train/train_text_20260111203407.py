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

# ---------------- LOAD DATASETS ----------------

print("📂 Loading GoEmotions CSV files...")

g1 = pd.read_csv("datasets/goemotions_1.csv")
g2 = pd.read_csv("datasets/goemotions_2.csv")
g3 = pd.read_csv("datasets/goemotions_3.csv")

goemo = pd.concat([g1, g2, g3], ignore_index=True)

# ----------- GOEMOTIONS LABEL EXTRACTION -----------

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

# ----------- PROCESS GOEMOTIONS -----------

print("🔄 Processing GoEmotions labels...")

goemo["emotion"] = goemo.apply(extract_goemotion, axis=1)
goemo_final = goemo[["text", "emotion"]]

# ----------- PROCESS EMOBANK -----------

print("🔄 Processing EmoBank labels...")

# EmoBank usually has 'emotion' OR 'valence'
if "emotion" not in emobank.columns:
    emobank["emotion"] = "neutral"

emobank_final = emobank[["text", "emotion"]]

# ----------- COMBINE DATASETS -----------

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

# ---------------- FEATURE EXTRACTION ----------------

print("🧠 Initializing TextEmotionDetector...")
detector = TextEmotionDetector()

print("🔎 Extracting BERT embeddings (this may take time)...")

X = []
for i, text in enumerate(texts):
    try:
        emb = detector.get_bert_embedding(text)
        pooled = np.mean(emb, axis=1)[0]
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

X_train = X_train.reshape(-1, 768, 1)
X_test = X_test.reshape(-1, 768, 1)

# ---------------- TRAIN MODEL ----------------

print("🚀 Training BERT + CNN/LSTM hybrid model...")

classifier = detector.classifier

classifier.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

history = classifier.fit(
    X_train,
    y_train,
    epochs=5,
    batch_size=16,
    validation_split=0.1,
    verbose=1
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

model_path = "../saved_models/text_emotion_hybrid.h5"
classifier.save(model_path)

print(f"\n✅ Text Emotion Model saved at: {model_path}")
print("🎉 Text Emotion Training Complete.")
