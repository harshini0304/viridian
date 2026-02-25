import os
import numpy as np
import tensorflow as tf
import librosa
from sklearn.metrics import classification_report
from models.audio_emotion_model import CNN_LSTM_Emotion, AudioEmotionDetector

print("Preparing audio datasets...")

DATA_FOLDER = "../datasets/audio"

# This script assumes you will place audio files like:
# viridian/datasets/audio/ravdess/
# viridian/datasets/audio/cremad/
# viridian/datasets/audio/tess/

def load_audio_features(base_path, label):
    X = []
    y = []

    for file in os.listdir(base_path):
        if file.endswith(".wav"):
            path = os.path.join(base_path, file)

            try:
                signal, sr = librosa.load(path, sr=None)
                mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=40)

                X.append(mfcc.T)
                y.append(label)

            except Exception:
                continue

    return X, y


X_all = []
y_all = []

print("Loading RAVDESS...")
x1, y1 = ravdess = load_audio_features("../datasets/audio/ravdess/", 0)

print("Loading CREMA-D...")
x2, y2 = load_audio_features("../datasets/audio/cremad/", 2)

print("Loading TESS...")
x3, y3 = load_audio_features("../datasets/audio/tess/", 5)

for x in x1 + x2 + x3:
    X_all.append(x)

y_all = np.array(y1 + y2 + y3)

print("Total audio samples:", len(X_all))

# Pad sequences to same length
max_len = max([x.shape[0] for x in X_all])

X_padded = []
for x in X_all:
    pad = np.pad(x, ((0, max_len - x.shape[0]), (0, 0)))
    X_padded.append(pad)

X_padded = np.array(X_padded)

num_classes = 6

print("Training audio CNN+LSTM model...")

model = CNN_LSTM_Emotion()

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(X_padded, y_all, epochs=10, batch_size=16)

print("Evaluation...")

pred = model.predict(X_padded)
y_pred = np.argmax(pred, axis=1)

print(classification_report(y_all, y_pred))

print("Saving audio model...")

os.makedirs("../saved_models", exist_ok=True)
model.save("../saved_models/audio_emotion_hybrid.h5")

print("Audio Training Complete.")
