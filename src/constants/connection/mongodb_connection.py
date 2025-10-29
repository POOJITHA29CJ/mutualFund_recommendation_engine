from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()


def get_mongo_connection():
    uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB")
    collection_name = os.getenv("MONGO_COLLECTION")

    client = MongoClient(uri)
    db = client[db_name]
    return db[collection_name]


def get_mongo_connection_for_fund():
    uri = "mongodb://localhost:27017"
    db_name = "fundDB"
    collection_name = "fund_structured"

    client = MongoClient(uri)
    db = client[db_name]
    return db[collection_name]
