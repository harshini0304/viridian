from datasets import load_dataset
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from models.text_emotion_model import TextEmotionDetector
import os

# ----------- LOAD DATASET -----------

print("Downloading GoEmotions from Hugging Face...")
ds = load_dataset("google-research-datasets/go_emotions", "simplified")

train_data = ds["train"]
test_data = ds["test"]

texts = train_data["text"]
labels = train_data["label"]

print("Total training samples:", len(texts))

# ----------- FEATURE EXTRACTION -----------

print("Initializing detector...")
detector = TextEmotionDetector()

print("Extracting BERT embeddings...")

X = []
y = []

for i, text in enumerate(texts):
    try:
        emb = detector.get_bert_embedding(text)

        # pooling to 768 dimension vector
        pooled = np.mean(emb, axis=1)[0]

        X.append(pooled)
        y.append(labels[i])

    except Exception as e:
        X.append(np.zeros(768))
        y.append(5)

X = np.array(X)
y = np.array(y)

print("Embedding shape:", X.shape)

# ----------- TRAIN TEST SPLIT -----------

print("Splitting data into train and validation...")

X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

X_train = X_train.reshape(len(X_train), 768, 1)
X_val = X_val.reshape(len(X_val), 768, 1)

# ----------- TRAIN CLASSIFIER -----------

print("Training hybrid BERT + CNN/LSTM model...")

classifier = detector.classifier

classifier.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

classifier.fit(X_train, y_train, epochs=5, batch_size=16)

# ----------- EVALUATION -----------

print("Evaluating on validation set...")

pred = classifier.predict(X_val)
y_pred = np.argmax(pred, axis=1)

print("Classification Report:\n")
print(classification_report(y_val, y_pred))

print("Computing metrics...")
precision, recall, f1, _ = precision_recall_fscore_support(y_val, y_pred, average='weighted')
acc = accuracy_score(y_val, y_pred)

metrics = {
    "accuracy": float(acc),
    "precision": float(precision),
    "f1_score": float(f1)
}

print("Final Metrics:", metrics)

# ----------- SAVE TRAINED MODEL -----------

print("Saving trained model...")

os.makedirs("saved_models", exist_ok=True)

classifier.save("saved_models/text_emotion_hybrid.h5")

print("Training Complete.")
