from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    notes = db.Column(db.String(255), default="")
    priority = db.Column(db.Integer, default=1)
