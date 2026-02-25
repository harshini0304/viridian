import numpy as np
import tensorflow as tf
import librosa
import soundfile as sf
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
import os


# ----------- AUDIO CNN + LSTM HYBRID MODEL -----------

class CNN_LSTM_Emotion(tf.keras.Model):

    def __init__(self, num_classes=6):
        super(CNN_LSTM_Emotion, self).__init__()

        self.conv1 = tf.keras.layers.Conv1D(64, 5, activation='relu')
        self.pool1 = tf.keras.layers.MaxPooling1D(2)

        self.conv2 = tf.keras.layers.Conv1D(128, 5, activation='relu')
        self.pool2 = tf.keras.layers.MaxPooling1D(2)

        self.lstm = tf.keras.layers.LSTM(128)

        self.dense = tf.keras.layers.Dense(64, activation='relu')
        self.out = tf.keras.layers.Dense(num_classes, activation='softmax')

    def call(self, inputs):

        x = self.conv1(inputs)
        x = self.pool1(x)

        x = self.conv2(x)
        x = self.pool2(x)

        x = self.lstm(x)
        x = self.dense(x)

        return self.out(x)


# ----------- FEATURE EXTRACTION CLASS -----------

class AudioEmotionDetector:

    def __init__(self):
        self.model = CNN_LSTM_Emotion()

        self.emotions = ["anger","joy","sadness","fear","love","neutral"]

    def extract_features(self, file_path):

        signal, sr = librosa.load(file_path, sr=None)

        mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=40)

        # transpose to CNN format
        return mfcc.T

    def predict_audio(self, file_path):

        feat = self.extract_features(file_path)

        feat = np.array([feat])

        pred = self.extract(np.array(feat))

        emotion = np.argmax(pred)

        return self.emotions[int(emotion)]

    def evaluate_audio(self, y_true, y_pred):

        print(classification_report(y_true, y_pred))

        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted')

        acc = accuracy_score(y_true, y_pred)

        return {
            "accuracy": float(acc),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1)
        }
