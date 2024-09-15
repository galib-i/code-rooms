from flask import Flask, render_template, url_for
from flask_socketio import SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


if __name__ == "__main__":
    socketio.run(app, debug=True)
