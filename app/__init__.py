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

        try:
            body = request.get_data(as_text=True)
            if body:
                app.logger.info(f'Body: {body}')

        except Exception as e:
            app.logger.error(f'Error parsing JSON: {e}')

    # Import and register the blueprints
    from app.routes import filemanager_bp
    app.register_blueprint(filemanager_bp, url_prefix='/api/v1/filemanager')
    @app.get('/')
    def index():
        return jsonify({'status': 'service is running'}), 200

    return app