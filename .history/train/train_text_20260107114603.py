import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
from models.text_emotion_model import TextEmotionDetector
import os

# ----------- LOAD YOUR DOWNLOADED DATASETS -----------

print("Loading local GoEmotions CSV files...")

g1 = pd.read_csv("../datasets/goemotions_1.csv")
g2 = pd.read_csv("../datasets/goemotions_2.csv")
g3 = pd.read_csv("../datasets/goemotions_3.csv")

goemo = pd.concat([g1, g2, g3])

print("Loading EmoBank dataset...")
emobank = pd.read_csv("../datasets/emobank.csv")

# Final combined dataset
data = pd.concat([goemo[["text","emotion"]], emobank[["text","emotion"]]])

texts = data["text"].astype(str).tolist()
labels = data["emotion"].tolist()

# ----------- MAP TO 6 EMOTION CLASSES -----------

label_map = {
    "anger":0,
    "joy":1,
    "sadness":2,
    "fear":3,
    "love":4,
    "neutral":5
}

y = np.array([label_map.get(l,5) for l in labels])

# ----------- FEATURE EXTRACTION -----------

print("Initializing detector...")
detector = TextEmotionDetector()

print("Extracting BERT embeddings...")

X = []
for t in texts:
    try:
        emb = detector.get_bert_embedding(t)
        pooled = np.mean(emb, axis=1)[0]
        X.append(pooled)
    except Exception:
        X.append(np.zeros(768))

X = np.array(X)

print("Dataset shape:", X.shape)

# ----------- TRAIN TEST SPLIT -----------

print("Splitting data...")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

X_train = X_train.reshape(len(X_train), 768, 1)
X_test = X_test.reshape(len(X_test), 768, 1)

# ----------- TRAIN MODEL -----------

print("Training hybrid BERT + CNN/LSTM classifier...")

classifier = detector.classifier

classifier.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

classifier.fit(X_train, y_train, epochs=5, batch_size=16)

# ----------- EVALUATION -----------

print("Evaluating model...")

pred = classifier.predict(X_test)
y_pred = np.argmax(pred, axis=1)

print(classification_report(y_test, y_pred))

precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')

metrics = {
    "accuracy": float(accuracy_score(y_test, y_pred)),
    "precision": float(precision),
    "recall": float(recall),
    "f1_score": float(f1)
}

print("Final Metrics:", metrics)

# ----------- SAVE MODEL -----------

os.makedirs("../saved_models", exist_ok=True)

classifier.save("../saved_models/text_emotion_hybrid.h5")

print("Training Complete.")
