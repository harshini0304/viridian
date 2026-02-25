import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from models.text_emotion_model import TextEmotionDetector

# ----------- LOAD DATASETS -----------

print("Loading GoEmotions dataset...")
goemo = pd.read_csv("datasets/goemotions.csv")

print("Loading EmoBank dataset...")
emobank = pd.read_csv("datasets/emobank.csv")

# combine both
data = pd.concat([goemo, emobank])

# assume both datasets have: columns -> text, emotion
texts = data["text"].astype(str).tolist()
labels = data["emotion"].tolist()

# map emotions to numeric classes
label_map = {
    "anger":0,
    "joy":1,
    "sadness":2,
    "fear":3,
    "love":4,
    "neutral":5
}

y = [label_map.get(l,5) for l in labels]

# ----------- PREPROCESS USING BERT -----------

detector = TextEmotionDetector()

print("Extracting BERT embeddings for all texts...")

X = []
for t in texts:
    try:
        emb = detector.get_bert_embedding(t)
        pooled = np.mean(emb, axis=1)
        X.append(pooled[0])
    except Exception as e:
        X.append(np.zeros(768))

X = np.array(X)
y = np.array(y)

# ----------- TRAIN TEST SPLIT -----------

print("Splitting data...")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

X_train = X_train.reshape(len(X_train), 768, 1)
X_test = X_test.reshape(len(X_test), 768, 1)

# ----------- BUILD CLASSIFIER -----------

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

report = classification_report(y_test, y_pred)

print(report)

print("Computing metrics...")
metrics = detector.evaluate(y_test, y_pred)

print("Final Metrics:", metrics)

# ----------- SAVE TRAINED MODEL -----------

print("Saving trained model...")

classifier.save("saved_models/text_emotion_hybrid.h5")

print("Training Complete.")
