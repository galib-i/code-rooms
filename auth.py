from flask import Blueprint, render_template, url_for, request, redirect
from flask_login import login_user, login_required, logout_user, current_user
from pymongo.errors import DuplicateKeyError

from db_connection import save_user, get_user

auth_bp = Blueprint("auth", __name__)


def redirect_if_logged_in():
    if current_user.is_authenticated:
        return redirect(url_for("home"))


@auth_bp.route("/register/", methods=["GET", "POST"])
def register():
    if redirect_if_logged_in():
        return redirect_if_logged_in()

    if request.method == "POST":
        try:
            save_user(username=request.form.get("username"),
                      email=request.form.get("email"),
                      password=request.form.get("password"))
            return redirect(url_for("auth.login"))

        except DuplicateKeyError:
            return render_template("register.html", error="Username already exists!")

    return render_template("register.html")


@auth_bp.route("/login/", methods=["GET", "POST"])
def login():
    if redirect_if_logged_in():
        return redirect_if_logged_in()

    if request.method == "POST":
        username = request.form.get("username")
        password_input = request.form.get("password")
        user = get_user(username)

        if user and user.check_password(password=password_input):
            login_user(user)
            return redirect(url_for("home"))
        return render_template("login.html", error="Error! Try again.")

    return render_template("login.html")


@auth_bp.route("/logout/", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))
