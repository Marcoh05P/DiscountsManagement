import hashlib
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import logout_user, current_user
from flask import redirect, url_for, request
from wtforms import PasswordField
from wtforms.validators import DataRequired, Optional
from DiscountsManagementApp import app, db, dao, utils
from .models import Promotion, User, UserRole, Order, PromotionType, OrderStatus
from wtforms.validators import DataRequired, NumberRange, ValidationError

class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login_view', next=request.url))

    def handle_view_exception(self, exc):
        db.session.rollback()
        return super().handle_view_exception(exc)

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
        form.full_name.validators = [DataRequired(message='Full name is required')]
        form.phone_number.validators = [DataRequired(message='Phone number is required'), utils.validate_phone_number]
        form.password.validators = [DataRequired(message='Password is required'), utils.validate_password]
        return form

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        form.password.validators = [Optional(), utils.validate_password]
        return form

    def on_form_prefill(self, form, id):
        form.password.data = ''

    def on_model_change(self, form, model, is_created):
        raw_password = (form.password.data or '').strip()
        if raw_password:
            model.password_hash = str(hashlib.md5(raw_password.encode('utf-8')).hexdigest())
            
    def delete_model(self, model):
        try:
            model.active = False
            db.session.add(model)
            db.session.commit()
            return True
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            return False

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

    def get_query(self):
        return super().get_query().filter(Promotion.active.is_(True))

    def get_count_query(self):
        return super().get_count_query().filter(Promotion.active.is_(True))
    
    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.code.validators = [DataRequired(message='Promotion code is required')]
        form.start_date.validators = [DataRequired(message='Start date is required')]
        form.expire_date.validators = [DataRequired(message='Expire date is required'), utils.validate_dates]
        form.value.validators = [NumberRange(min=0, message='Value must be non-negative'), utils.validate_promotion_value]
        form.availability_count.validators = [NumberRange(min=1, message='Availability count must be at least 1')]
        form.max_discount_amount.render_kw = {}
        form.max_discount_amount.validators = [
            NumberRange(min=0, message='Max discount amount must be non-negative'),
            utils.validate_max_discount_amount,
        ]
        form.min_order_value.validators = [NumberRange(min=0, message='Min order value must be non-negative')]
        return form
    
    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        form.code.render_kw = {'readonly': True}
        # Do not use disabled for select fields because disabled inputs are not submitted.
        # Keep it effectively read-only in UI and preserve value on backend in on_model_change.
        form.promotion_type.render_kw = {
            'style': 'pointer-events:none;background-color:#eeeeee;',
            'tabindex': '-1',
        }
        form.start_date.validators = [DataRequired(message='Start date is required')]
        form.expire_date.validators = [DataRequired(message='Expire date is required'), utils.validate_dates]
        form.value.validators = [NumberRange(min=0, message='Value must be non-negative'), utils.validate_promotion_value]
        form.availability_count.validators = [NumberRange(min=1, message='Availability count must be at least 1')]
        form.min_order_value.validators = [NumberRange(min=0, message='Min order value must be non-negative')]
        if utils.is_coupon(form.promotion_type.data):
            form.max_discount_amount.render_kw = {}
            form.max_discount_amount.validators = [
                DataRequired(message='Max discount amount is required for COUPON type'),
                NumberRange(min=0, message='Max discount amount must be non-negative'),
                utils.validate_max_discount_amount,
            ]
        else:
            form.max_discount_amount.render_kw = {'readonly': True}
        return form
    
    def on_model_change(self, form, model, is_created):
        if not is_created:
            existing = Promotion.query.get(model.id)
            if existing is not None:
                model.promotion_type = existing.promotion_type

        if model.expire_date <= model.start_date:
            raise ValidationError('Expire date must be after start date.')
        if model.value is None or model.value <= 0:
            raise ValidationError('Value must be greater than 0.')

        if utils.is_coupon(model.promotion_type):
            if model.value > 0.5:
                raise ValidationError('For COUPON type, value must be at most 0.5.')
            if model.max_discount_amount is None or model.max_discount_amount <= 0:
                raise ValidationError('Max discount amount is required for COUPON type.')
        else:
            model.max_discount_amount = model.value
        
    def on_form_prefill(self, form, id):
        form.value.data = float(form.value.data) if form.value.data is not None else None
        if form.max_discount_amount.data is not None:
            form.max_discount_amount.data = float(form.max_discount_amount.data)
        elif not utils.is_coupon(form.promotion_type.data):
            form.max_discount_amount.data = form.value.data

    def delete_model(self, model):
        try:
            model.active = False
            db.session.add(model)
            db.session.commit()
            return True
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            return False

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