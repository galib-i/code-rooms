import random

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user

from .database import (save_room, delete_room, get_room, get_room_members,
                       add_room_member, get_joined_rooms)

rooms_bp = Blueprint("rooms", __name__)


def generate_unique_room_code():
    """Creates a random 5-digit code as the room_code when creating a room"""
    while True:
        random_number = random.randint(0, 99999)
        new_code = f"{random_number:05d}"  # pads with zeros if >5 digits

        if not get_room(room_code=new_code):
            return new_code


def redirect_to_room(room_code):
    """Redirects to the room page if the user is a member or owner"""
    room = get_room(room_code=room_code)
    if not room or (current_user.username != room["owner"]
                    and current_user.username not in get_room_members(room_code=room_code)):

        return redirect(url_for("home"))

    is_owner = current_user.username == room["owner"]
    return render_template("open-room.html", room_code=room_code, is_owner=is_owner)


def handle_join_request():
    """Handles the POST request for join_room()"""
    room_code = request.form.get("room-code")
    if get_room(room_code=room_code):
        if current_user.username not in get_room_members(room_code=room_code):
            add_room_member(room_code=room_code, username=current_user.username)

        return redirect(url_for("rooms.view_room", room_code=room_code))

    return render_template("join-room.html", error="Room not found!")


@rooms_bp.route("/open-room/", methods=["GET"])
@login_required
def open_room():
    """Creates a new room and redirects the owner to the room page"""
    new_code = generate_unique_room_code()
    save_room(room_code=new_code, owner=current_user.username)

    return redirect(url_for("rooms.view_room", room_code=new_code))


@rooms_bp.route("/room/<room_code>", methods=["GET"])
@login_required
def view_room(room_code):
    """If the room code is valid, opens the room page"""
    return redirect_to_room(room_code=room_code)


@rooms_bp.route("/join-room/", methods=["GET", "POST"])
@login_required
def join_room():
    """Allows a user to join a room using the room code"""
    if request.method == "POST":
        return handle_join_request()

    rooms = []
    data = get_joined_rooms(username=current_user.username)
    joined_room_codes = [room["room_code"] for room in data]

    for room_code in joined_room_codes:
        room_info = get_room(room_code=room_code)

        is_owner = current_user.username == room_info["owner"]
        members = get_room_members(room_code=room_code)

        room = {"room_code": room_code, "members": members, "is_owner": is_owner}
        rooms.append(room)

    return render_template("join-room.html", rooms=rooms)


@rooms_bp.route("/delete-room/", methods=["POST"])
@login_required
def delete_current_room():
    """Allows the owner to delete the current room"""
    room_code = request.json.get("room_code")
    if current_user.username == get_room(room_code=room_code)["owner"]:
        delete_room(room_code)

    return jsonify({})
