import sys
import random
from io import StringIO

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user

from .db_connection import save_room, get_room, get_room_members, add_room_member
rooms_bp = Blueprint("rooms", __name__)


def generate_code():
    """Generate a random 5-digit code as the room ID"""
    while True:
        random_number = random.randint(0, 99999)
        code = f"{random_number:05d}"  # pads with zeros if >5 digits

        if not get_room(code):
            return code


@rooms_bp.route("/open-room/", methods=["GET"])
@login_required
def open_room():
    """Create a new room and redirect the owner to the room page"""
    code = generate_code()
    save_room(room_code=code, owner=current_user.username)

    return redirect(url_for("rooms.open_room_code", code=code))


@rooms_bp.route("/room/<code>", methods=["GET"])
@login_required
def open_room_code(code):
    room = get_room(code)
    if not room:
        return redirect(url_for("home"))

    if current_user.username != room["owner"]:
        members = [member["username"] for member in get_room_members(code)]
        if current_user.username not in members:
            return redirect(url_for("home"))

    return render_template("open-room.html", room_code=code)


@rooms_bp.route("/join-room/", methods=["GET", "POST"])
@login_required
def join_room():
    if request.method == "POST":
        code = request.form.get("room-code")
        try:
            get_room(code)["_id"]
            add_room_member(room_code=code, username=current_user.username)
            return redirect(url_for("rooms.open_room_code", code=code))

        except TypeError:
            return render_template("join-room.html", error="Room not found!")

    return render_template("join-room.html")


@rooms_bp.route("/run-python-code", methods=["POST"])
@login_required
def run_python_code():
    code = request.json.get("code")
    old_stdout = sys.stdout
    redirected_output = StringIO()
    sys.stdout = redirected_output

    try:
        exec(code)
    except Exception as e:
        output = str(e)
    else:
        output = redirected_output.getvalue()
    finally:
        sys.stdout = old_stdout

    return jsonify({"output": output})
