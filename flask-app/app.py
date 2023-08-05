from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# Flask 애플리케이션 객체 생성
app = Flask(__name__)

# JWT 설정
app.config["JWT_SECRET_KEY"] = "your-secret-key"  # TODO: JWT 시크릿
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db' # TODO: Database URI

# SQLAlchemy와 Migrate 초기화
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# JWT 확장 초기화
jwt = JWTManager(app)

# 라우트와 모델을 불러옵니다.
import routes
# import models
