from flask import Flask, Blueprint, jsonify
from pymongo import MongoClient
from typing import Type
import atexit

from config import Config as DefaultConfig
from .extensions import cors, jwt, swaggerui_bp

def create_app(config_object: Type[DefaultConfig] = DefaultConfig) -> Flask:
    app = Flask(__name__, static_folder="public", static_url_path="/public")
    app.config.from_object(config_object)

    cors.init_app(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Type", "Authorization"],
    )

    jwt.init_app(app)
    _register_jwt_error_handlers(app)

    mongo_client = MongoClient(app.config["MONGO_URI"])
    db = mongo_client.get_database()
    app.mongo_client = mongo_client
    app.mongo_db = db

    atexit.register(mongo_client.close)

    _register_blueprints(app, db)
    return app

def _register_blueprints(app: Flask, db):
    api_bp = Blueprint("api", __name__, url_prefix="/api")

    @api_bp.get("/")
    def root():
        return jsonify({"message": "'Gloup Gloup' I'm Sardine and this is my API !"}), 200

    from src.app.auth import create_auth_router
    api_bp.register_blueprint(create_auth_router(db), url_prefix="/auth")

    from src.app.users import create_users_router
    api_bp.register_blueprint(create_users_router(db), url_prefix="/users")

    from src.app.playgrounds import create_playgrounds_router
    api_bp.register_blueprint(create_playgrounds_router(db), url_prefix="/playgrounds")

    from src.app.playgrounds_prompts import create_playgrounds_prompts_router
    api_bp.register_blueprint(create_playgrounds_prompts_router(db), url_prefix="/playgrounds")

    from src.app.models import create_models_router
    api_bp.register_blueprint(create_models_router(db), url_prefix="/models")

    from src.app.configurations import create_configurations_router
    api_bp.register_blueprint(create_configurations_router(db), url_prefix="/configurations")

    from src.app.data import create_data_router
    api_bp.register_blueprint(create_data_router(db), url_prefix="/data")

    app.register_blueprint(swaggerui_bp)
    app.register_blueprint(api_bp)

def _register_jwt_error_handlers(app: Flask):
    from flask import jsonify
    from .extensions import jwt

    @jwt.unauthorized_loader
    def _unauthorized(msg):
        return jsonify({"error": "authorization_required", "message": msg}), 401

    @jwt.invalid_token_loader
    def _invalid(msg):
        return jsonify({"error": "invalid_token", "message": msg}), 422

    @jwt.expired_token_loader
    def _expired(jwt_header, jwt_payload):
        return jsonify({"error": "token_expired", "message": "Access token has expired"}), 401

    @jwt.needs_fresh_token_loader
    def _needs_fresh(jwt_header, jwt_payload):
        return jsonify({"error": "fresh_token_required"}), 401

    @jwt.revoked_token_loader
    def _revoked(jwt_header, jwt_payload):
        return jsonify({"error": "token_revoked"}), 401