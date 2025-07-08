from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)  # Optional: allow cross-origin if you're using React or another frontend

    from app.routes import api
    app.register_blueprint(api)

    return app