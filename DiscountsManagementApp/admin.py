import hashlib
from datetime import datetime

from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView, typefmt
from flask_admin.theme import Bootstrap4Theme
from flask_login import logout_user, current_user
from flask import redirect, url_for, request
from markupsafe import Markup
from wtforms import PasswordField
from wtforms.validators import DataRequired, Optional
from DiscountsManagementApp import app, db, dao, validators
from .models import Promotion, User, UserRole, Order, PromotionType, OrderStatus
from wtforms.validators import DataRequired, NumberRange, ValidationError
from .validators.admin.field_validators import validate_phone_number_field, validate_password_field, \
    validate_date_field, validate_promotion_value_field, validate_max_discount_amount_field, \
    is_existing_order_using_promotion
from .validators.base import is_coupon


def date_format(view, value):
    return value.strftime('%d/%m/%Y %H:%M:%S')


DATETIME_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
DATETIME_FORMATTERS.update({
    datetime: date_format
})

def format_datetime_view(v, c, m, p):
    value = getattr(m, p)
    if value:
        formatted_date = date_format(None, value)
        return Markup(f'<span style="min-width: 150px; display: inline-block;">{formatted_date}</span>')
    return ""


class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login_view', next=request.url))

    def handle_view_exception(self, exc):
        db.session.rollback()
        return super().handle_view_exception(exc)

    column_type_formatters = DATETIME_FORMATTERS

class UserView(AuthenticatedModelView):
    column_list = ('id', 'full_name', 'phone_number', 'role', 'active')
    column_searchable_list = ['full_name', 'phone_number']
    column_filters = ['role']
    column_labels = {
        'full_name': 'Họ và tên',
        'phone_number': 'Số điện thoại',
        'role': 'Vai trò',
        'active': 'Kích hoạt'
    }
    form_columns = ('full_name', 'phone_number', 'role', 'password', 'active')
    column_exclude_list = ['password_hash']
    form_extra_fields = {
        'password': PasswordField('Password')
    }

    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.full_name.validators = [DataRequired(message='Họ và tên là bắt buộc')]
        form.phone_number.validators = [DataRequired(message='Số điện thoại là bắt buộc'),
                                        validate_phone_number_field]
        form.password.validators = [DataRequired(message='Mật khẩu là bắt buộc'), validate_password_field]
        return form

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        form.role.render_kw = {'style': 'pointer-events:none;background-color:#eeeeee;', 'tabindex': '-1'}
        form.password.validators = [Optional(), validate_password_field]
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
    column_list = ('id', 'code', 'promotion_type', 'start_date', 'expire_date', 'availability_count', 'value',
                   'max_discount_amount', 'min_order_value', 'description')
    column_searchable_list = ['code']
    column_filters = ['promotion_type']
    column_labels = {
        'code': 'Mã khuyến mãi',
        'promotion_type': 'Loại khuyến mãi',
        'start_date': 'Ngày bắt đầu',
        'expire_date': 'Ngày hết hạn',
        'availability_count': 'Số lượng còn lại',
        'value': 'Giá trị giảm',
        'max_discount_amount': 'Số tiền giảm tối đa',
        'min_order_value': 'Giá trị đơn tối thiểu',
        'description': 'Mô tả'
    }
    form_columns = ('code', 'promotion_type', 'start_date', 'expire_date', 'availability_count', 'value',
                    'max_discount_amount', 'min_order_value', 'description')

    form_args = {
        'start_date': {'format': '%d/%m/%Y %H:%M'},
        'expire_date': {'format': '%d/%m/%Y %H:%M'},
    }
    form_widget_args = {
        'start_date': {'data-date-format': 'DD/MM/YYYY HH:mm'},
        'expire_date': {'data-date-format': 'DD/MM/YYYY HH:mm'},
    }

    column_formatters = {
        'start_date': format_datetime_view,
        'expire_date': format_datetime_view
    }

    def get_query(self):
        return super().get_query().filter(Promotion.active.is_(True))

    def get_count_query(self):
        return super().get_count_query().filter(Promotion.active.is_(True))

    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.code.validators = [DataRequired(message='Mã khuyến mãi là bắt buộc')]
        form.start_date.validators = [DataRequired(message='Ngày bắt đầu là bắt buộc')]
        form.expire_date.validators = [DataRequired(message='Ngày hết hạn là bắt buộc'), validate_date_field]
        form.value.validators = [NumberRange(min=0, message='Giá trị phải lớn hơn hoặc bằng 0'),
                                 validate_promotion_value_field]
        form.availability_count.validators = [NumberRange(min=1, message='Số lượng còn lại phải ít nhất là 1')]
        form.max_discount_amount.render_kw = {}
        form.max_discount_amount.validators = [
            NumberRange(min=0, message='Giảm tối đa phải lớn hơn hoặc bằng 0'),
            validate_max_discount_amount_field,
        ]
        form.min_order_value.validators = [NumberRange(min=0, message='Giá trị đơn tối thiểu phải lớn hơn hoặc bằng 0')]
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
        form.start_date.validators = [DataRequired(message='Ngày bắt đầu là bắt buộc')]
        form.expire_date.validators = [DataRequired(message='Ngày hết hạn là bắt buộc'), validate_date_field]
        form.value.validators = [NumberRange(min=0, message='Giá trị phải lớn hơn hoặc bằng 0'),
                                 validate_promotion_value_field]
        form.availability_count.validators = [NumberRange(min=1, message='Số lượng còn lại phải ít nhất là 1')]
        form.min_order_value.validators = [NumberRange(min=0, message='Giá trị đơn tối thiểu phải lớn hơn hoặc bằng 0')]
        if is_coupon(form.promotion_type.data):
            form.max_discount_amount.render_kw = {}
            form.max_discount_amount.validators = [
                DataRequired(message='Giảm tối đa là bắt buộc với loại COUPON'),
                NumberRange(min=0, message='Giảm tối đa phải lớn hơn hoặc bằng 0'),
                validate_max_discount_amount_field,
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
            raise ValidationError('Ngày hết hạn phải sau ngày bắt đầu.')
        if model.value is None or model.value <= 0:
            raise ValidationError('Giá trị phải lớn hơn 0.')

        if is_coupon(model.promotion_type):
            if model.value > 0.5:
                raise ValidationError('Với loại COUPON, giá trị tối đa là 0.5.')
            if model.max_discount_amount is None or model.max_discount_amount <= 0:
                raise ValidationError('Giảm tối đa là bắt buộc với loại COUPON.')
        else:
            model.max_discount_amount = model.value

    def on_form_prefill(self, form, id):
        form.value.data = float(form.value.data) if form.value.data is not None else None
        if form.max_discount_amount.data is not None:
            form.max_discount_amount.data = float(form.max_discount_amount.data)
        elif not is_coupon(form.promotion_type.data):
            form.max_discount_amount.data = form.value.data

    def delete_model(self, model):
        try:
            if (is_existing_order_using_promotion(model)):
                raise ValidationError('Không thể xóa khuyến mãi vì đã có đơn hàng sử dụng.')
            model.active = False
            db.session.add(model)
            db.session.commit()
            return True
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            return False


class OrdersView(AuthenticatedModelView):
    can_create = False
    column_list = ('id', 'customer_id', 'promotion_id', 'created_date', 'sub_total_amount', 'discount_amount',
                   'final_amount', 'status')
    column_searchable_list = ['customer_id']
    column_filters = ['status']
    column_labels = {
        'customer_id': 'Khách hàng',
        'promotion_id': 'Khuyến mãi',
        'created_date': 'Ngày tạo',
        'sub_total_amount': 'Tạm tính',
        'discount_amount': 'Giảm giá',
        'final_amount': 'Thành tiền',
        'status': 'Trạng thái'
    }
    form_columns = ('customer_id', 'promotion_id', 'created_date', 'sub_total_amount', 'discount_amount',
                    'final_amount', 'status')

    form_args = {
        'created_date': {'format': '%d/%m/%Y %H:%M'}
    }
    form_widget_args = {
        'created_date': {'data-date-format': 'DD/MM/YYYY HH:mm'}
    }

    column_formatters = {
        'created_date': format_datetime_view
    }

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        form.customer_id.render_kw = {'readonly': True}
        form.promotion_id.render_kw = {'readonly': True}
        form.created_date.render_kw = {'readonly': True}
        form.sub_total_amount.render_kw = {'readonly': True}
        form.discount_amount.render_kw = {'readonly': True}
        form.final_amount.render_kw = {'readonly': True}
        return form


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect(url_for('index'))

    def is_accessible(self):
        return current_user.is_authenticated


admin = Admin(app=app, name='Discounts Management', theme=Bootstrap4Theme(fluid=True))
admin.add_view(UserView(User, db.session))
admin.add_view(PromotionView(Promotion, db.session))
admin.add_view(OrdersView(Order, db.session))
admin.add_view(LogoutView(name='Logout', endpoint='logout', category=None))
