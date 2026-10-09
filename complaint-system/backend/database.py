from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='student')   # student | admin
    hostel = db.Column(db.String(50), nullable=True)
    room_number = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    complaints = db.relationship('Complaint', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)


class Complaint(db.Model):
    __tablename__ = 'complaints'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default='Open')   # Open|In Progress|Resolved|Rejected
    severity = db.Column(db.String(20), default='Medium')  # Low|Medium|High|Critical
    hostel = db.Column(db.String(50), nullable=True)
    room_number = db.Column(db.String(20), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    is_preventive = db.Column(db.Boolean, default=False)
    is_fake = db.Column(db.Boolean, default=False)
    fake_score = db.Column(db.Float, default=0.0)   # 0-1 probability of being fake
    is_repeat = db.Column(db.Boolean, default=False)
    repeat_count = db.Column(db.Integer, default=0)
    original_complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=True)
    admin_notes = db.Column(db.Text, nullable=True)
    estimated_cost = db.Column(db.Float, nullable=True)
    actual_cost = db.Column(db.Float, nullable=True)
    assigned_to = db.Column(db.String(100), nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reviews = db.relationship('Review', backref='complaint', lazy=True)


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)   # 1-5
    comment = db.Column(db.Text, nullable=True)
    sentiment = db.Column(db.String(20), nullable=True)  # positive|neutral|negative
    sentiment_score = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class HotspotData(db.Model):
    __tablename__ = 'hotspot_data'
    id = db.Column(db.Integer, primary_key=True)
    hostel = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    complaint_count = db.Column(db.Integer, default=0)
    avg_resolution_days = db.Column(db.Float, default=0.0)
    risk_score = db.Column(db.Float, default=0.0)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    computed_at = db.Column(db.DateTime, default=datetime.utcnow)


class CostForecast(db.Model):
    __tablename__ = 'cost_forecasts'
    id = db.Column(db.Integer, primary_key=True)
    hostel = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=True)
    forecast_month = db.Column(db.Integer, nullable=False)
    forecast_year = db.Column(db.Integer, nullable=False)
    predicted_complaints = db.Column(db.Integer, default=0)
    estimated_cost = db.Column(db.Float, default=0.0)
    actual_cost = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50), nullable=True)
    target_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
