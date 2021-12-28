from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

db = SQLAlchemy()
migrate = Migrate()
load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__)

    app.url_map.strict_slashes = False
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Configure JWT manager
    app.config["SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
    JWTManager(app)

    # Configure database 
    if test_config is None:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "SQLALCHEMY_DATABASE_URI")
    else:
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "SQLALCHEMY_TEST_DATABASE_URI")

    # Import models here for Alembic setup
    from app.models.flashcard import Flashcard
    from app.models.deck import Deck
    from app.models.user import User 

    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints 
    from app.routes import decks_bp
    app.register_blueprint(decks_bp)

    from app.routes import flashcards_bp
    app.register_blueprint(flashcards_bp)

    from app.routes import users_bp
    app.register_blueprint(users_bp)

    from app.routes import app_bp
    app.register_blueprint(app_bp)

    CORS(app)
    return app
