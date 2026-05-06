import json
import os
from datetime import datetime, timedelta
import logging
from logging.config import dictConfig

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, get_jwt, create_access_token, get_jwt_identity
from init import bcrypt, jwt, pymongo, cors, init_app
from service.LoginUser import LoginUser
from view.authentication import auth
from view.audioProcess import audio
from dotenv import load_dotenv


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

# load environment variables
load_dotenv()

# initalize flask app
app = Flask(__name__)
app.register_blueprint(auth, url_prefix='/api')
app.register_blueprint(audio, url_prefix='/audio')

# config the app
app.config.update({
    'DEBUG': os.getenv('FLASK_DEBUG', 'false').lower() == 'true',
    'JWT_SECRET_KEY': os.getenv('SECRET_KEY', 'THISWILLBECHANGELATERON'),
    'JWT_TOKEN_LOCATION': 'headers',
    'JWT_ACCESS_TOKEN_EXPIRES': timedelta(days=1),
    'MONGO_URI': os.getenv('MONGO_URI', 'mongodb://127.0.0.1:27017/annotation_tool_healthcare_dialogue?authSource=admin'),
    'CORS_HEADERS': 'Content-Type',
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,
})
#

def page_not_found(e):
    """Custom error handling for 404"""
    return jsonify({"error": "page not found"})

init_app(app)


app.register_error_handler(404, page_not_found)

logging.getLogger('flask_cors').level = logging.DEBUG

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
#
# if __name__ != '__main__':
#     gunicorn_logger = logging.getLogger('gunicorn.error')
#     app.logger.handlers = gunicorn_logger.handlers
#     app.logger.setLevel(gunicorn_logger.level)

if __name__ != '__main__':

    gunicorn_logger = logging.getLogger('gunicorn.error')

    if gunicorn_logger.hasHandlers():
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    app.logger.info("Gunicorn logging configured correctly.")



if __name__ == '__main__':
    load_dotenv()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "4000")))
