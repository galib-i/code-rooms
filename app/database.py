import os

from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

from app.user import User

load_dotenv()
client = MongoClient(os.getenv("URI"))  # store in .env file as URI=".."
db = client.get_database(os.getenv("DB_NAME"))  # store in .env file as DB_NAME=".."

users = db.get_collection("users")
rooms = db.get_collection("rooms")
room_members = db.get_collection("room_members")
editor_codes = db.get_collection("editor_codes")
messages = db.get_collection("messages")


# Functions related to the user
def save_user(username, email, password):
    """Stores the user data in the database"""
    hashed_password = generate_password_hash(password=password)
    users.insert_one({"_id": username, "email": email, "password": hashed_password})


def get_user(username):
    """Returns a User object from the database"""
    user_data = users.find_one({"_id": username})

    return User(user_data["_id"], user_data["email"],
                user_data["password"]) if user_data else None


# Functions related to the rooms
def save_room(room_code, owner):
    """Stores newly created room in the database"""
    rooms.insert_one({"_id": room_code, "owner": owner})  # identifies room owners
    add_room_member(room_code=room_code, username=owner)


def delete_room(room_code):
    """Deletes the room and its members from the database"""
    rooms.delete_one({"_id": room_code})
    room_members.delete_many({"room_code": room_code})


def get_room(room_code):
    """Checks if the room exists in the database

    Returns:
        pymongo.cursor.Cursor(obj) or None: object with room code and owner username
    """
    return rooms.find_one({"_id": room_code})


# Functions related to the room members
def get_joined_rooms(username):
    """Finds the rooms the user has joined

    Returns:
        pymongo.cursor.Cursor(obj) or None: object with joined room codes
    """
    return room_members.find({"username": username})


def get_room_members(room_code):
    """Returns a list of usernames of the members of the room"""
    return [member["username"] for member in
            room_members.find({"room_code": room_code})]


def add_room_member(room_code, username):
    """Adds a user to the room"""
    room_members.insert_one({"room_code": room_code, "username": username})


# Functions related to the chat
def save_message(room_code, sender, text):
    """Stores the message in the database - MongoDB's ObjectId contains a timestamp,
    they are sorted by the time they were inserted"""
    messages.insert_one({"room_code": room_code, "sender": sender, "text": text})


def get_messages(room_code):
    """Returns a list of messages in the room"""
    return list(messages.find({"room_code": room_code}))


# Functions related to the editor
def save_editor_code(room_code, editor_code, output):
    """Stores the code in the database"""
    editor_codes.replace_one(
        {"_id": room_code}, {"_id": room_code, "code": editor_code, "output": output}, upsert=True)


def get_editor_code(room_code):
    """Returns the code and output from the database"""
    editor_data = editor_codes.find_one({"_id": room_code})
    code = editor_data["code"] if editor_data else ""
    output = editor_data["output"] if editor_data else ""

    return code, output
