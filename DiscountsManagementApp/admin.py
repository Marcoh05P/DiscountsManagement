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
        'full_name': 'Họ và tên',
        'phone_number': 'Số điện thoại',
        'role': 'Vai trò',
        'active': 'Hoạt động'
    }
    form_columns = ('full_name', 'phone_number', 'role', 'password', 'active')
    column_exclude_list = ['password_hash']
    form_extra_fields = {
        'password': PasswordField('Mật khẩu')
    }

    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.password.validators = [DataRequired(message='Mật khẩu là bắt buộc')]
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
        'code': 'Mã khuyến mãi',
        'promotion_type': 'Loại khuyến mãi',
        'start_date': 'Ngày bắt đầu',
        'expire_date': 'Ngày hết hạn',
        'availability_count': 'Số lượng',
        'value': 'Giá trị',
        'max_discount_amount': 'Giảm tối đa',
        'min_order_value': 'Giá trị đơn tối thiểu',
        'description': 'Mô tả'
    }
    form_columns = ('code', 'promotion_type', 'start_date', 'expire_date', 'availability_count', 'value', 'max_discount_amount', 'min_order_value', 'description')

class OrdersView(AuthenticatedModelView):
    column_list = ('id', 'customer_id', 'promotion_id', 'created_date', 'sub_total_amount', 'discount_amount', 'final_amount', 'status')
    column_searchable_list = ['customer_id']
    column_filters = ['status']
    column_labels = {
        'customer_id': 'Khách hàng',
        'promotion_id': 'Khuyến mãi',
        'created_date': 'Ngày tạo',
        'sub_total_amount': 'Tổng tiền',
        'discount_amount': 'Giảm giá',
        'final_amount': 'Thành tiền',
        'status': 'Trạng thái'
    }
    form_columns = ('customer_id', 'promotion_id', 'created_date', 'sub_total_amount', 'discount_amount', 'final_amount', 'status')
    
    

admin = Admin(app=app, name='Quản trị Discounts Management')
admin.add_view(UserView(User, db.session))
admin.add_view(PromotionView(Promotion, db.session))
admin.add_view(OrdersView(Order, db.session))