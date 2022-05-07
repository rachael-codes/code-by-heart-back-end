from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_cors import CORS
import os

db = SQLAlchemy()
migrate = Migrate()
load_dotenv()


def create_app():
    app = Flask(__name__)
    
    app.url_map.strict_slashes = False
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['CORS_HEADERS'] = 'Content-Type'

    # Configure database 
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")

    # Import models here for Alembic setup
    from app.models.client import Client
    from app.models.flashcard import Flashcard
    from app.models.deck import Deck

    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints 
    from app.routes.other_routes import app_bp
    app.register_blueprint(app_bp)
    
    from app.routes.deck_routes import decks_bp
    app.register_blueprint(decks_bp)

    from app.routes.flashcard_routes import flashcards_bp
    app.register_blueprint(flashcards_bp)

    CORS(app)
    return app
