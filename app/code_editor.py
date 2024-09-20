import sys
from io import StringIO

from flask import Blueprint, jsonify, request
from flask_socketio import SocketIO, emit
from flask_login import login_required

socketio = SocketIO()
code_editor_bp = Blueprint("code_editor", __name__)


@code_editor_bp.route("/run-python-code", methods=["POST"])
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


@socketio.on("code_update")
def handle_code_update(data):
    emit("update_editor", {"code": data["code"]}, broadcast=True)
