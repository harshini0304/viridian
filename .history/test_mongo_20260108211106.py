from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME")

print("Connecting to MongoDB...")
client = MongoClient(uri, serverSelectionTimeoutMS=5000)

db = client[db_name]

print("Databases:", client.list_database_names())

test_col = db.test_collection
result = test_col.insert_one({"status": "mongo_connected"})
print("Insert successful, id:", result.inserted_id)

client.close()
print("MongoDB connection SUCCESS ✅")
