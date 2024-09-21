import os

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_login import LoginManager, current_user

from .authentication import auth_bp
from .rooms import rooms_bp
from .code_editor import socketio, code_editor_bp
from .database import get_user


login_manager = LoginManager()
load_dotenv()


def create_app():
    """Creates a Flask app and initialises the socketio instance"""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    socketio.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(code_editor_bp)

    @app.route("/")
    def home():
        username = current_user.username if current_user.is_authenticated else "there"
        return render_template("index.html", logged_in=current_user.is_authenticated, user=username)

    return app


@login_manager.user_loader
def load_user(username):
    return get_user(username)
