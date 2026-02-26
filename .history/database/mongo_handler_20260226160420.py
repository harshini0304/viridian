from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
from bson.objectid import ObjectId
from requests import session
from sympy import limit

load_dotenv()


class MongoHandler:
    def __init__(self):
        uri = os.getenv("MONGO_URI")
        db_name = os.getenv("DB_NAME")

        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.db = self.client[db_name]

        # collections
        self.sessions = self.db.sessions

        print("MongoHandler initialized successfully")

    def create_session(self, username):
        session = {
            "username": username,
            "created_at": datetime.utcnow(),
            "messages": [],
            "emotions": []
        }
        result = self.sessions.insert_one(session)
        return str(result.inserted_id)

    def add_message(self, session_id, text, sender):
        self.sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$push": {
                "messages": {
                    "sender": sender,
                    "text": text,
                    "timestamp": datetime.utcnow()
                }
            }}
        )

    def add_emotion(self, session_id, emotion_data):
        self.sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$push": {
                "emotions": {
                    **emotion_data,
                    "timestamp": datetime.utcnow()
                }
            }}
        )

    def get_session_history(self, session_id):
        return self.sessions.find_one({"_id": ObjectId(session_id)})
  
    def get_recent_messages(self, session_id, limit=5):
        session = self.sessions.find_one({"_id": session_id})
        if not session:
            return []

        return session.get("messages", [])[-limit:]
     