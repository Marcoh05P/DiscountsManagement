from wtforms import ValidationError

from DiscountsManagementApp.models import Order
from DiscountsManagementApp.validators.base import validate_order_update, validate_password_value, validate_date_range, \
    validate_promotion_value, validate_max_discount_amount, validate_phone_number


def validate_date_field(form, field):
    if form.start_date.data and field.data:
        is_valid, error_message = validate_date_range(form.start_date.data, field.data)
        if not is_valid:
            raise ValidationError(error_message)


def validate_promotion_value_field(form, field):
    value = field.data
    promotion_type = form.promotion_type.data
    is_valid, error_message = validate_promotion_value(value, promotion_type)
    if not is_valid:
        raise ValidationError(error_message)


def validate_max_discount_amount_field(form, field):
    max_discount_value = field.data
    promotion_type = form.promotion_type.data
    min_order_value = form.min_order_value.data
    promotion_value = form.value.data
    is_valid, error_message = validate_max_discount_amount(max_discount_value, promotion_type, min_order_value,
                                                           promotion_value)
    if not is_valid:
        raise ValidationError(error_message)


def validate_phone_number_field(form, field):
    phone_number = field.data
    is_valid, error_message = validate_phone_number(phone_number)
    if not is_valid:
        raise ValidationError(error_message)


def validate_password_field(form, field):
    password = (field.data or '').strip()
    is_valid, error_message = validate_password_value(password)
    if not is_valid:
        raise ValidationError(error_message)


def is_existing_order_using_promotion(promotion):
    return Order.query.filter(Order.promotion_id == promotion.id, Order.status == 'PENDING').first() is not None


def validate_order_update_status_field(form, field):
    order = form._obj
    new_status = field.data
    if order and new_status:
        is_valid, error_message = validate_order_update(customer_id=order.customer_id, old_status=order.status.name, new_status=new_status)
        if not is_valid:
            raise ValidationError(error_message)
