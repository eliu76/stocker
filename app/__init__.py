from flask import Flask
from flask_cors import CORS

from src.models.watchlist_model import db
from src.routes.watchlist_api import watchlist_bp
from app.routes import api

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Database setup
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///watchlist.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Register both route blueprints
    app.register_blueprint(api, url_prefix="/api")          # stock analysis
    app.register_blueprint(watchlist_bp, url_prefix="/api") # watchlist

    return app
