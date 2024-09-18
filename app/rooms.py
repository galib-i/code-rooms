import sys
import random
from io import StringIO

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user

from .db_connection import save_room, get_room, get_room_members
rooms_bp = Blueprint("rooms", __name__)


def generate_code():
    """Generate a random 5-digit code for the room"""
    while True:
        random_number = random.randint(0, 99999)
        code = f"{random_number:05d}"  # pads with zeros if >5 digits

        if not get_room(code)["_id"]:
            return code


@rooms_bp.route("/open-room/", methods=["GET"])
@login_required
def open_room():
    code = generate_code()
    save_room(room_code=code, owner=current_user.username)

    return redirect(url_for('rooms.open_room_code', code=code))


@rooms_bp.route("/room/<code>", methods=["GET"])
@login_required
def open_room_code(code):
    if current_user.username != get_room(code)["owner"]:
        return redirect(url_for("rooms.join_room"))
    return render_template("open-room.html", room_code=code)


@rooms_bp.route("/run-code", methods=["POST"])
@login_required
def run_code():
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


@rooms_bp.route("/join-room/", methods=["GET", "POST"])
@login_required
def join_room():
    return render_template("join-room.html")
