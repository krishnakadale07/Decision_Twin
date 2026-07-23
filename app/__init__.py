from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import Config
from app.database import db

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)

    # Register Blueprints
    from app.routes import auth_bp, decisions_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(decisions_bp)

    @app.route('/api/health')
    def health_check():
        return {"status": "ok", "message": "Backend is running!"}, 200

    return app