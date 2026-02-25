import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Dense, Concatenate, Dropout
from tensorflow.keras.models import Model


class FusionEmotionModel(Model):
    """
    Fusion model that combines:
    - Text features (BERT embeddings)
    - Audio features (CNN+LSTM output)
    """

    def __init__(self, num_classes=6):
        super(FusionEmotionModel, self).__init__()

        self.concat = Concatenate()
        self.fc1 = Dense(256, activation="relu")
        self.dropout1 = Dropout(0.3)

        self.fc2 = Dense(128, activation="relu")
        self.dropout2 = Dropout(0.3)

        self.output_layer = Dense(num_classes, activation="softmax")

    def call(self, inputs):
        """
        inputs = [text_features, audio_features]
        """

        text_feat, audio_feat = inputs

        x = self.concat([text_feat, audio_feat])
        x = self.fc1(x)
        x = self.dropout1(x)

        x = self.fc2(x)
        x = self.dropout2(x)

        return self.output_layer(x)


class FusionEmotionDetector:
    """
    Wrapper class for prediction and evaluation
    """

    def __init__(self):
        self.model = FusionEmotionModel()
        self.emotions = ["anger", "joy", "sadness", "fear", "love", "neutral"]

    def predict(self, text_embedding, audio_embedding):
        """
        text_embedding: shape (1, 768)
        audio_embedding: shape (1, N)
        """

        prediction = self.model([text_embedding, audio_embedding])
        emotion_id = int(np.argmax(prediction))
        confidence = float(np.max(prediction))

        return self.emotions[emotion_id], confidence
