from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from flask_cors import CORS

bcrypt = Bcrypt()
pymongo = PyMongo()
jwt = JWTManager()
cors = CORS()
