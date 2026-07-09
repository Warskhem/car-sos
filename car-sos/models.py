from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class QRCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    is_claimed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    claimed_at = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    user = db.relationship('User', backref=db.backref('qr_codes', lazy=True))
    vehicle = db.relationship('Vehicle', backref='qr_code', uselist=False, lazy=True)

    def __repr__(self):
        return f'<QRCode {self.code}>'

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    qr_code_id = db.Column(db.Integer, db.ForeignKey('qr_code.id'), nullable=False, unique=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    plate = db.Column(db.String(20), nullable=False)
    color = db.Column(db.String(30), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('vehicles', lazy=True))

    def __repr__(self):
        return f'<Vehicle {self.plate}>'

class EmergencyContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    priority = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref=db.backref('emergency_contacts', lazy=True))

    def __repr__(self):
        return f'<EmergencyContact {self.name}>'

class SOSLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qr_code_id = db.Column(db.Integer, db.ForeignKey('qr_code.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    rescuer_lat = db.Column(db.Float, nullable=True)
    rescuer_lng = db.Column(db.Float, nullable=True)
    contacted_at = db.Column(db.DateTime, default=datetime.utcnow)
    call_status = db.Column(db.String(20), default='pending')

    qr_code_rel = db.relationship('QRCode', backref=db.backref('sos_logs', lazy=True))
    vehicle_rel = db.relationship('Vehicle', backref=db.backref('sos_logs', lazy=True))

    def __repr__(self):
        return f'<SOSLog {self.id} - {self.contacted_at}>'
