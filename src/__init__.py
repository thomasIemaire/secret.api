from flask import Flask, Blueprint, jsonify
from pymongo import MongoClient
from typing import Type
import atexit

from config import Config as DefaultConfig
from .extensions import cors, jwt, swaggerui_bp

def create_app(config_object: Type[DefaultConfig] = DefaultConfig) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    cors.init_app(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    jwt.init_app(app)

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

    from src.app.agents import create_agents_router
    api_bp.register_blueprint(create_agents_router(db), url_prefix="/agents")

    from src.app.users import create_users_router
    api_bp.register_blueprint(create_users_router(db), url_prefix="/users")

    app.register_blueprint(swaggerui_bp)
    app.register_blueprint(api_bp)