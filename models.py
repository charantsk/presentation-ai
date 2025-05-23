# models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class FileRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(120), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)
    file_data = db.Column(db.Text, nullable=False)
