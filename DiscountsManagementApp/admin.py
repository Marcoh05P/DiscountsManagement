import hashlib
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import logout_user, current_user
from flask import redirect, url_for, request
from wtforms import PasswordField
from wtforms.validators import DataRequired, Optional
from DiscountsManagementApp import app, db, dao, utils
from .models import Promotion, User, UserRole, Order, PromotionType, OrderStatus

class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login_view', next=request.url))

class UserView(AuthenticatedModelView):
    column_list = ('id', 'full_name', 'phone_number', 'role', 'active')
    column_searchable_list = ['full_name', 'phone_number']
    column_filters = ['role']
    column_labels = {
        'full_name': 'Full Name',
        'phone_number': 'Phone Number',
        'role': 'Role',
        'active': 'Active'
    }
    form_columns = ('full_name', 'phone_number', 'role', 'password', 'active')
    column_exclude_list = ['password_hash']
    form_extra_fields = {
        'password': PasswordField('Password')
    }

    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.password.validators = [DataRequired(message='Password is required')]
        return form

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        form.password.validators = [Optional()]
        return form

    def on_form_prefill(self, form, id):
        form.password.data = ''

    def on_model_change(self, form, model, is_created):
        raw_password = (form.password.data or '').strip()
        if raw_password:
            model.password_hash = str(hashlib.md5(raw_password.encode('utf-8')).hexdigest())

class PromotionView(AuthenticatedModelView):
    column_list = ('id', 'code', 'promotion_type', 'start_date', 'expire_date', 'availability_count', 'value', 'max_discount_amount', 'min_order_value', 'description')
    column_searchable_list = ['code']
    column_filters = ['promotion_type']
    column_labels = {
        'code': 'Promotion Code',
        'promotion_type': 'Promotion Type',
        'start_date': 'Start Date',
        'expire_date': 'Expire Date',
        'availability_count': 'Availability Count',
        'value': 'Value',
        'max_discount_amount': 'Max Discount Amount',
        'min_order_value': 'Min Order Value',
        'description': 'Description'
    }
    form_columns = ('code', 'promotion_type', 'start_date', 'expire_date', 'availability_count', 'value', 'max_discount_amount', 'min_order_value', 'description')

class OrdersView(AuthenticatedModelView):
    column_list = ('id', 'customer_id', 'promotion_id', 'created_date', 'sub_total_amount', 'discount_amount', 'final_amount', 'status')
    column_searchable_list = ['customer_id']
    column_filters = ['status']
    column_labels = {
        'customer_id': 'Customer',
        'promotion_id': 'Promotion',
        'created_date': 'Created Date',
        'sub_total_amount': 'Sub Total Amount',
        'discount_amount': 'Discount Amount',
        'final_amount': 'Final Amount',
        'status': 'Status'
    }
    form_columns = ('customer_id', 'promotion_id', 'created_date', 'sub_total_amount', 'discount_amount', 'final_amount', 'status')

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect(url_for('index'))
    
    def is_accessible(self):
        return current_user.is_authenticated

admin = Admin(app=app, name='Discounts Management')
admin.add_view(UserView(User, db.session))
admin.add_view(PromotionView(Promotion, db.session))
admin.add_view(OrdersView(Order, db.session))
admin.add_view(LogoutView(name='Logout', endpoint='logout', category=None))