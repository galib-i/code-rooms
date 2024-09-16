from flask import Blueprint, render_template
from flask_login import login_required

rooms_bp = Blueprint("rooms", __name__)


@rooms_bp.route("/create-room/", methods=["GET"])
@login_required
def create_room():
    return render_template("create-room.html")


@rooms_bp.route("/join-room/", methods=["GET"])
@login_required
def join_room():
    return render_template("join-room.html")
