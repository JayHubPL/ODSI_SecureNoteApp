from flask import Flask, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address)


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '3ac49319d0663de0787139911449e5366695510c80da7ab0b03aeff1b3908ecd'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}
    app.config['SESSION_COOKIE_SECURE'] = True,
    app.config['SESSION_COOKIE_HTTPONLY'] = True,
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'

    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .share import share as share_blueprint
    app.register_blueprint(share_blueprint)

    from .encrypt import encrypt as encrypt_blueprint
    app.register_blueprint(encrypt_blueprint)

    from .note_view import note_view as note_view_blueprint
    app.register_blueprint(note_view_blueprint)

    return app
