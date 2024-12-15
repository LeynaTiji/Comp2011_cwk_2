from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__, template_folder="templates",static_folder="static")
app.config.from_object('config')
app.config['DEBUG'] = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from app import views, models, forms
from app.models import Film

with app.app_context():
    if Film.query.count() == 0:
        views.data_csv_into_db()