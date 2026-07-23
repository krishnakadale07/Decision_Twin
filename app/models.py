from app.database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    decisions = db.relationship('Decision', backref='owner', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Decision(db.Model):
    __tablename__ = 'decisions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    options = db.relationship('Option', backref='decision', lazy=True, cascade="all, delete-orphan")
    criteria = db.relationship('Criterion', backref='decision', lazy=True, cascade="all, delete-orphan")


class Option(db.Model):
    __tablename__ = 'options'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    decision_id = db.Column(db.Integer, db.ForeignKey('decisions.id'), nullable=False)

    scores = db.relationship('Score', backref='option', lazy=True, cascade="all, delete-orphan")


class Criterion(db.Model):
    __tablename__ = 'criteria'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, default=1.0)  # e.g., 1.0 to 10.0 weight factor
    decision_id = db.Column(db.Integer, db.ForeignKey('decisions.id'), nullable=False)

    scores = db.relationship('Score', backref='criterion', lazy=True, cascade="all, delete-orphan")


class Score(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)  # Rating/Score given to an option against a criterion
    option_id = db.Column(db.Integer, db.ForeignKey('options.id'), nullable=False)
    criterion_id = db.Column(db.Integer, db.ForeignKey('criteria.id'), nullable=False)