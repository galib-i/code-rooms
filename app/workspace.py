import sys
from io import StringIO

from flask import Blueprint, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import login_required, current_user

from .database import save_message, get_messages, save_editor_code, get_editor_code

socketio = SocketIO()
workspace_bp = Blueprint("workspace", __name__)


@workspace_bp.route("/run-python-code", methods=["POST"])
@login_required
@socketio.on("run_code")
def handle_run_code(data):
    """Executes Python code and broadcasts the output to all users in the room"""
    editor_code = data.get("code")
    room_code = data.get("room_code")
    old_stdout = sys.stdout  # saves the current standard output
    # redirects the output to a StringIO object to capture it
    redirected_output = StringIO()
    sys.stdout = redirected_output

    try:
        exec(editor_code)
        output = redirected_output.getvalue()
    except Exception as e:
        output = str(e)  # if there's an error in the code, displays it as an output
    finally:
        sys.stdout = old_stdout

    emit("code_output", {"output": output}, room=room_code)


@socketio.on("editor_code_update")
def handle_editor_code_update(data):
    """Broadcasts the updated code to all users in the room"""
    emit("update_editor", {"code": data["code"]}, room=data["room_code"])


@socketio.on("join_room")
def handle_join_room_event(data):
    """Connects the user to the specified room and announces it"""
    room_code = data["room_code"]
    chat_history = get_messages(room_code=room_code)
    # formats the chat history, for it to be sent to the user
    chat_data = [{"username": message["sender"], "message": message["text"]}
                 for message in chat_history]
    editor_code, output = get_editor_code(room_code=room_code)

    join_room(room=room_code)
    # only loads the editor code and chat history to the user who joined
    emit("load_editor_code", {"code": editor_code, "output": output}, room=request.sid)
    emit("chat_history", {"messages": chat_data}, room=request.sid)
    emit("join_room_announcement", data, room=room_code)


@socketio.on("leave_room")
def handle_leave_room_event(data):
    """Disconnects the user from the specified room and announces it"""
    room_code = data["room_code"]
    save_editor_code(room_code, data["editor_code"], data["output"])

    leave_room(room=room_code)
    emit("leave_room_announcement", data, room=room_code)


@socketio.on("send_message")
def handle_send_message_event(data):
    """Handles sending a message to the chat and broadcasts it to the room"""
    room_code = data["room_code"]
    message = data["message"]
    username = current_user.username

    save_message(room_code=room_code, sender=username, text=message)
    emit("receive_message", {"username": username, "message": message}, room=room_code)
