from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = 'APTX4869'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/discounts_db?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 8

db = SQLAlchemy(app=app)
login_manager = LoginManager()
login_manager.init_app(app)

login = login_manager

@login_manager.user_loader
def load_user(user_id):
	from DiscountsManagementApp.models import User

	return User.query.get(int(user_id))

@login_manager.request_loader
def load_user_from_request(request):
	from DiscountsManagementApp import dao
	auth = request.authorization

	if auth and auth.type == 'basic':
		return dao.auth_user(auth.username, auth.password)
	return None
