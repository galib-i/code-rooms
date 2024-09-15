from flask import Flask, render_template, url_for, request, redirect
from flask_socketio import SocketIO
from pymongo.errors import DuplicateKeyError
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from db_connection import save_user, get_user

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            save_user(username=username, email=email, password=password)
            return redirect(url_for("login"))
        except DuplicateKeyError:
            return render_template("register.html", error="Username already exists!")

    return render_template("register.html")


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password_input = request.form.get("password")
        user = get_user(username)

        if user and user.check_password(password=password_input):
            login_user(user)
            return redirect(url_for('home'))

    return render_template("login.html", error="Error! Try again.")


@login_manager.user_loader
def load_user(username):
    return get_user(username)


if __name__ == "__main__":
    socketio.run(app, debug=True)
