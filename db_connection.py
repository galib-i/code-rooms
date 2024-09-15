import os

from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

from user import User

load_dotenv()
client = MongoClient(os.getenv("URI"))

db = client.get_database("code_chat")
users = db.get_collection("users")


def save_user(username, email, password):
    hashed_password = generate_password_hash(password=password)
    users.insert_one({"_id": username, "email": email, "password": hashed_password})


def get_user(username):
    user_data = users.find_one({"_id": username})
    return User(user_data["_id"], user_data["email"], user_data["password"]) if user_data else None
