# DB interaction helper functions
# app/models.py
from datetime import datetime
from . import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    click_x = db.Column(db.Integer)
    click_y = db.Column(db.Integer)
    click_x_norm = db.Column(db.Float)   # optional
    click_y_norm = db.Column(db.Float)   # optional
    image_filename = db.Column(db.String(255), default='auth_image.jpg')
    secret_color = db.Column(db.String(10))
    color_sequence = db.Column(db.String(32))
    level2_passed = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    logs = db.relationship('BehaviorLog', backref='user', cascade="all, delete-orphan")

class BehaviorLog(db.Model):
    __tablename__ = 'behavior_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50))
    data = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
