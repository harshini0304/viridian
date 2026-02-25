import os
import numpy as np
import tensorflow as tf
import librosa
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
from models.audio_emotion_model import CNN_LSTM_Emotion

# ======================================================
# PATH SETUP (ROBUST – WORKS WITH python -m)
# ======================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, "datasets", "audio")

RAVDESS_PATH = os.path.join(DATASET_DIR, "ravdess")
CREMAD_PATH = os.path.join(DATASET_DIR, "cremad")
TESS_PATH = os.path.join(DATASET_DIR, "tess")

# ======================================================
# LOAD AUDIO FEATURES
# ======================================================

def load_audio_features(folder_path, label):
    X, y = [], []

    if not os.path.exists(folder_path):
        print(f"[WARNING] Folder not found: {folder_path}")
        return X, y

    for file in os.listdir(folder_path):
        if file.lower().endswith(".wav"):
            file_path = os.path.join(folder_path, file)
            try:
                signal, sr = librosa.load(file_path, sr=None)
                mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=40)
                X.append(mfcc.T)
                y.append(label)
            except Exception as e:
                print("Error processing:", file_path)

    return X, y

# ======================================================
# LOAD DATASETS
# ======================================================

print("Preparing audio datasets...")

X_all, y_all = [], []

print("Loading RAVDESS...")
x1, y1 = load_audio_features(RAVDESS_PATH, 0)   # anger
print("Samples:", len(x1))

print("Loading CREMA-D...")
x2, y2 = load_audio_features(CREMAD_PATH, 2)    # sadness
print("Samples:", len(x2))

print("Loading TESS...")
x3, y3 = load_audio_features(TESS_PATH, 5)      # neutral
print("Samples:", len(x3))

X_all = x1 + x2 + x3
y_all = np.array(y1 + y2 + y3)

print("Total audio samples:", len(X_all))

# ======================================================
# PAD MFCC SEQUENCES
# ======================================================

max_len = max(x.shape[0] for x in X_all)

X_padded = []
for x in X_all:
    pad_width = max_len - x.shape[0]
    padded = np.pad(x, ((0, pad_width), (0, 0)))
    X_padded.append(padded)

X_padded = np.array(X_padded)

print("Final input shape:", X_padded.shape)

# ======================================================
# MODEL TRAINING
# ======================================================

print("Building CNN + LSTM audio model...")

model = CNN_LSTM_Emotion(num_classes=6)

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.fit(
    X_padded,
    y_all,
    epochs=5,        # reduce if system is slow
    batch_size=8
)

# ======================================================
# EVALUATION
# ======================================================

print("Evaluating model...")

pred = model.predict(X_padded)
y_pred = np.argmax(pred, axis=1)

print(classification_report(y_all, y_pred))

precision, recall, f1, _ = precision_recall_fscore_support(
    y_all, y_pred, average="weighted"
)

metrics = {
    "accuracy": float(accuracy_score(y_all, y_pred)),
    "precision": float(precision),
    "recall": float(recall),
    "f1_score": float(f1)
}

print("Final Metrics:", metrics)

# ======================================================
# SAVE MODEL
# ======================================================

SAVE_DIR = os.path.join(BASE_DIR, "saved_models")
os.makedirs(SAVE_DIR, exist_ok=True)

model.save(os.path.join(SAVE_DIR, "audio_emotion_hybrid.h5"))

print("Audio Training Complete.")
