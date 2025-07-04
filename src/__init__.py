from flask import Flask, jsonify, Blueprint
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from config import Config
from pymongo import MongoClient

jwt = JWTManager()

swaggerui_bp = get_swaggerui_blueprint(
    '/swagger',
    '/static/swagger.json',
    config={ 'app_name': "Sardine's API" }
)

api_keys: list[str] = ["super_secret_key"]

def create_app() -> Flask:
    app = Flask(__name__)

    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    app.config.from_object(Config)

    jwt.init_app(app)

    mongo_client = MongoClient(app.config["MONGO_URI"])
    app.mongo = mongo_client.get_database()

    set_routes(app)

    return app

def set_routes(app: Flask) -> None:
    api_router = Blueprint('api', __name__, url_prefix='/api')

    @api_router.route("/", methods=["GET"])
    def init():
        return jsonify({ "message": "Welcome on Sardine's API !"}), 200
    
    app.register_blueprint(swaggerui_bp)

    from src.app.flows.flows_controller import create_flows_router
    from src.app.agents.agents_controller import create_agents_router
    from src.app.predicts.predicts_controller import create_predicts_router

    api_router.register_blueprint(create_flows_router(app.mongo), url_prefix='/flows')
    api_router.register_blueprint(create_agents_router(app.mongo), url_prefix='/agents')
    api_router.register_blueprint(create_predicts_router(app.mongo), url_prefix='/predicts')

    app.register_blueprint(api_router)