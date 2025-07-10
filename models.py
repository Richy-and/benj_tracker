from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Worker(db.Model):
    """Worker model for storing worker information"""
    __tablename__ = 'workers'
    
    id = db.Column(db.Integer, primary_key=True)
    matricule = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to attendance records
    attendance_records = db.relationship('Attendance', back_populates='worker', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Worker {self.matricule}: {self.name}>'

class Attendance(db.Model):
    """Attendance model for storing attendance records"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to worker
    worker = db.relationship('Worker', back_populates='attendance_records')
    
    # Ensure one attendance record per worker per day
    __table_args__ = (db.UniqueConstraint('worker_id', 'date', name='unique_worker_date'),)
    
    def __repr__(self):
        return f'<Attendance {self.worker.matricule} on {self.date}>'