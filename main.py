from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_login import LoginManager

from auth import auth_bp
from db_connection import get_user

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

app.register_blueprint(auth_bp)


@app.route("/")
def home():
    return render_template("index.html")


@login_manager.user_loader
def load_user(username):
    return get_user(username)


if __name__ == "__main__":
    socketio.run(app, debug=True)
