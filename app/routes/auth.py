from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.database import db
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "User with that username or email already exists"}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        # Create JWT access token with the user's ID as identity
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            "message": "Login successful!",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }), 200
    
    return jsonify({"error": "Invalid username or password"}), 401


# --- PROTECTED PROFILE ROUTES ---

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email
    }), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json() or {}
    
    if 'email' in data:
        # Check if email is already in use by another account
        existing = User.query.filter(User.email == data['email'], User.id != user.id).first()
        if existing:
            return jsonify({"error": "Email is already in use"}), 400
        user.email = data['email']

    if 'password' in data and data['password']:
        user.set_password(data['password'])

    db.session.commit()

    return jsonify({"message": "Profile updated successfully!"}), 200