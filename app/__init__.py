import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from dotenv import load_dotenv
import logging
from logging.handlers import TimedRotatingFileHandler
from flask_cors import CORS

from .services.model_loader import clean_model_cache

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    """
    Create a Flask application using the app factory pattern.
    :param config_class: Configuration class 
    :return:  Flask app
    """""
    load_dotenv()

    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    app.config.from_object(config_class)
    if not os.path.exists('logs'):
        os.mkdir('logs')

    # Logging configuration
    handler = TimedRotatingFileHandler(app.config['LOG_FILE'], when="midnight", interval=1, backupCount=7) # 1 week of logs retained
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO) # SQLAlchemy logging
    app.logger.addHandler(handler)

    app.logger.info('Microservice started')

    # Initialize the database
    from app.models import filemanager

    db.init_app(app)
    migrate.init_app(app, db)
    app.logger.info('Database initialized')

    @app.before_request
    def log_request_info():
        message = f'Handling request: {request.method} {request.url}'
        app.logger.info(message)

    # Import and register the blueprints
    from app.routes import filemanager_bp, predict_bp
    app.register_blueprint(filemanager_bp, url_prefix='/api/v1/filemanager')
    app.register_blueprint(predict_bp, url_prefix='/api/v1/predict')

    scheduler = BackgroundScheduler()
    if not any(job.name == "clean_model_cache_job" for job in scheduler.get_jobs()):
        scheduler.add_job(clean_model_cache, trigger='interval', hours=1, id='clean_model_cache_job')

    scheduler.start()

    # Define the routes
    @app.get('/')
    def index():
        return jsonify({'status': 'service is running'}), 200

    @app.get('/api/v1')
    def api_v1():
        return jsonify({'status': 'service is running'}), 200

    @app.get('/api/v1/gpu')
    def check_gpu():
        from app.services.checkGPUService import check_gpu
        return jsonify(check_gpu()), 200

    return app