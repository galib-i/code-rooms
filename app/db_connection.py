import os

from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

from app.user import User

load_dotenv()
client = MongoClient(os.getenv("URI"))

db = client.get_database(os.getenv("DB_NAME"))
users = db.get_collection("users")
rooms = db.get_collection("rooms")
room_members = db.get_collection("room_members")
python_code = db.get_collection("python_code")


def save_user(username, email, password):
    hashed_password = generate_password_hash(password=password)
    users.insert_one({"_id": username, "email": email, "password": hashed_password})


def get_user(username):
    user_data = users.find_one({"_id": username})
    return User(user_data["_id"], user_data["email"],
                user_data["password"]) if user_data else None


def save_room(room_code, owner):
    rooms.insert_one({"_id": room_code, "owner": owner})
    room_members.insert_one({"room_code": room_code, "username": owner})


def get_room(room_code):
    return rooms.find_one({"_id": room_code})


def get_room_members(room_code):
    return list(room_members.find({"room_code": room_code}))


def save_python_code(room_code, code):
    python_code.update_one({"room_code": room_code}, {"$set": {"code": code}},
                           upsert=True)
