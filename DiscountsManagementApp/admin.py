import hashlib
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import logout_user, current_user
from flask import redirect, url_for, request
from wtforms import FileField
from DiscountsManagementApp import app, db, dao, utils


admin = Admin(app=app, name='Quản trị Discounts Management')