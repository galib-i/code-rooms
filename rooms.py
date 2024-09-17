import sys
from io import StringIO

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required


rooms_bp = Blueprint("rooms", __name__)


@rooms_bp.route("/view-room/", methods=["GET", "POST"])
@login_required
def view_room():
    if request.method == "POST":
        code = request.json.get('code')
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

        return jsonify({'output': output})
    return render_template("view-room.html")


@rooms_bp.route("/join-room/", methods=["GET", "POST"])
@login_required
def join_room():
    return render_template("join-room.html")
