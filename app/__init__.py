from flask import Flask
from flask_cors import CORS

from src.models.watchlist_model import db
from src.routes.watchlist_api import watchlist_bp
from app.routes import api
from src.routes.digest_api import digest_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    # database setup
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///watchlist.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # register route blueprints
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(watchlist_bp, url_prefix="/api/watchlist")
    app.register_blueprint(digest_bp, url_prefix="/api/digest")

    return app
