from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_login import LoginManager, current_user

from auth import auth_bp
from rooms import rooms_bp
from db_connection import get_user

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(rooms_bp)


@app.route("/")
def home():
    username = current_user.username if current_user.is_authenticated else "there"
    return render_template("index.html", logged_in=current_user.is_authenticated, user=username)


@app.route
@login_manager.user_loader
def load_user(username):
    return get_user(username)


if __name__ == "__main__":
    socketio.run(app, debug=True)
