import sys
from io import StringIO

from flask import Blueprint, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import login_required, current_user

socketio = SocketIO()
workspace_bp = Blueprint("workspace", __name__)


@workspace_bp.route("/run-python-code", methods=["POST"])
@login_required
def run_python_code():
    """Runs the Python code in the editor and return the output"""
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


@socketio.on("editor_code_update")
def handle_editor_code_update(data):
    """Broadcasts the updated code to all users in the room"""
    emit("update_editor", {"code": data["code"]}, broadcast=True)


@socketio.on("join_room")
def handle_join_room_event(data):
    """Connects the user to the specified room and announces it"""
    join_room(data["room_id"])
    emit("join_room_announcement", data, room=data["room_id"])


@socketio.on("leave_room")
def handle_leave_room_event(data):
    """Disconnects the user from the specified room and announces it"""
    leave_room(data["room_id"])
    emit("leave_room_announcement", data, room=data["room_id"])


@socketio.on("send_message")
def handle_send_message_event(data):
    """Handles sending a message to the chat and broadcasts it to the room"""
    room_id = data["room_id"]
    message = data["message"]
    username = current_user.username
    emit("receive_message", {"username": username, "message": message}, room=room_id)
