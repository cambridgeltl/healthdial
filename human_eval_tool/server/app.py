# -*- coding: utf-8 -*-
"""
Flask App for Human Evaluation Tool - Main Entry Point
"""

import os
from datetime import datetime, timedelta
import logging
from logging.config import dictConfig
from pathlib import Path

from flask import Flask, jsonify, send_from_directory
from flask_jwt_extended import JWTManager, get_jwt, create_access_token, get_jwt_identity
from dotenv import load_dotenv

from init import bcrypt, jwt, pymongo, cors
from service.LoginUser import LoginUser
from view.authentication import auth

# -------------------- Logging Configuration --------------------
dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        },
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

# -------------------- Load Environment Variables --------------------
load_dotenv()


def _env_flag(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}

# -------------------- Initialize Flask App --------------------
app = Flask(__name__, static_folder=None)
app.register_blueprint(auth, url_prefix='/api')

# -------------------- App Configuration --------------------
app.config.update({
    'DEBUG': _env_flag('FLASK_DEBUG', default=True),
    'JWT_SECRET_KEY': os.getenv('SECRET_KEY', 'change-me-for-local-development'),
    'JWT_TOKEN_LOCATION': 'headers',
    'SECRET_KEY': os.getenv('SECRET_KEY', 'change-me-for-local-development'),
    'JWT_ACCESS_TOKEN_EXPIRES': timedelta(minutes=60),
    'MONGO_URI': os.getenv('MONGO_URI', 'mongodb://localhost:27017/health_dialogue_human_eval'),
    'CORS_HEADERS': 'Content-Type'
})

# -------------------- Init Services --------------------
bcrypt.init_app(app)
jwt.init_app(app)
pymongo.init_app(app)
cors.init_app(app)

# -------------------- React Static File Serving --------------------
CLIENT_BUILD_PATH = Path(__file__).resolve().parent.parent / 'client' / 'build'

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """
    Serves React build files. If not found, returns index.html for SPA support.
    """
    file_path = CLIENT_BUILD_PATH / path
    if file_path.exists() and file_path.is_file():
        return send_from_directory(CLIENT_BUILD_PATH, path)
    else:
        return send_from_directory(CLIENT_BUILD_PATH, 'index.html')


# -------------------- JWT Refresh Logic --------------------
@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        current_identity = get_jwt_identity()
        current_user = LoginUser().check_user_with_id(current_identity)

        now = datetime.now()
        target_timestamp = datetime.timestamp(now + timedelta(minutes=60))
        if target_timestamp > exp_timestamp:
            new_access_token = create_access_token(
                identity=current_identity,
                additional_claims={"role": current_user.role.model_dump()}
            )

            data = response.get_json()
            if isinstance(data, dict):
                data["access_token"] = new_access_token
                response = jsonify(data)

        return response
    except (RuntimeError, KeyError):
        return response

# -------------------- Health Check Endpoint --------------------
@app.route('/healthz')
def health_check():
    return jsonify({"status": "ok"}), 200

# -------------------- 404 Handler --------------------
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "page not found"}), 404

# -------------------- Run the App --------------------
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    app.run(host=os.getenv('HOST', '0.0.0.0'), port=int(os.getenv('PORT', '4000')))
