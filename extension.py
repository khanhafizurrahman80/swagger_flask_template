from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from passlib.context import CryptContext

from common.apispec import APISpecExt
from flask_sqlalchemy import SQLAlchemy


apispec = APISpecExt()
db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

