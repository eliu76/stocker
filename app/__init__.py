from flask import Flask
from flask_cors import CORS
from app.routes import api

def create_app():
    app = Flask(__name__)
    CORS(app)  # enable CORS for all routes

    app.register_blueprint(api, url_prefix="/api")  # must match the /api prefix in your React fetch

    return app