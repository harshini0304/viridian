from pymongo import MongoClient
from datetime import datetime
import os
from config import Config


class MongoHandler:

    def __init__(self):
        if not Config.MONGO_URI:
            raise Exception("MongoDB URI not configured")

        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]

    # ---------- SESSION MANAGEMENT ----------

    def create_session(self, username):
        session = {
            "username": username,
            "start_time": datetime.utcnow(),
            "messages": [],
            "emotions": []
        }
        result = self.db.sessions.insert_one(session)
        return str(result.inserted_id)

    def add_message(self, session_id, text, sender):
        message = {
            "text": text,
            "sender": sender,
            "time": datetime.utcnow()
        }
        self.db.sessions.update_one(
            {"_id": session_id},
            {"$push": {"messages": message}}
        )

    def add_emotion(self, session_id, emotion, confidence, modality):
        emo = {
            "emotion": emotion,
            "confidence": float(confidence),
            "modality": modality,
            "time": datetime.utcnow()
        }
        self.db.sessions.update_one(
            {"_id": session_id},
            {"$push": {"emotions": emo}}
        )

    # ---------- ANALYTICS ----------

    def get_session_history(self, session_id):
        return self.db.sessions.find_one({"_id": session_id})

    def get_user_sessions(self, username):
        return list(self.db.sessions.find({"username": username}))

    def close(self):
        self.client.close()
