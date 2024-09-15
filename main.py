from flask import Flask, render_template, url_for, request, redirect
from flask_socketio import SocketIO
from pymongo.errors import DuplicateKeyError

from db_connection import save_user

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login/")
def login():
    return render_template("login.html")


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


if __name__ == "__main__":
    socketio.run(app, debug=True)
