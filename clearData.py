from pymongo import MongoClient
import os
client = MongoClient(os.environ.get("MONGO_CONNECTION_STRING"))
db = client[os.environ.get("COLLECTION_NAME")]
remainders = db.remainders
remainders.remove()