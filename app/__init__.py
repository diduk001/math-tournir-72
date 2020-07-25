from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app)

# Создание и инициализация менеджера входа

login_manager = LoginManager()
login_manager.init_app(app)

db.create_all()
db.session.commit()

from app import routes, models
