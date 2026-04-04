from datetime import datetime

from DiscountsManagementApp import db
from DiscountsManagementApp.dao import create_user_promotion_usage
from wtforms.validators import ValidationError

from DiscountsManagementApp.models import Order, PromotionType

def is_coupon(value):
    if isinstance(value, PromotionType):
        return value == PromotionType.COUPON
    return str(value) == PromotionType.COUPON.value

def validate_registration_data(full_name, phone_number, password, confirm):
    if not full_name or not full_name.strip():
        return False, 'Họ và tên là bắt buộc!'
    if not phone_number or not phone_number.strip():
        return False, 'Số điện thoại là bắt buộc!'
    if not password:
        return False, 'Mật khẩu là bắt buộc!'
    if password != confirm:
        return False, 'Mật khẩu xác nhận không khớp!'
    return True, ''


def validate_order_data(user, sub_total_amount=None, promotion=None, promotion_usage=None, is_using_promotion=False, discount_amount=None):
    if sub_total_amount is None or sub_total_amount <= 0:
        return False, 'Giá trị đơn hàng không hợp lệ!'

    if not promotion and is_using_promotion:
        return False, 'Mã khuyến mãi không tồn tại!'
    if promotion.expire_date < datetime.now():
        return False, 'Mã khuyến mãi đã hết hạn!'
    if promotion.availability_count <= 0:
        return False, 'Mã khuyến mãi đã hết lượt sử dụng!'
    if promotion.min_order_value and sub_total_amount < promotion.min_order_value:
        return False, f'Giá trị đơn hàng phải lớn hơn hoặc bằng {promotion.min_order_value} để áp dụng!'
    if discount_amount and discount_amount >= (sub_total_amount / 2):
        return False, 'Không thể sử dụng mã khuyến mãi này vì giá trị giảm giá vượt quá 50% giá trị đơn hàng!'
    if promotion_usage and promotion_usage.usage_count >= 2:
        return False, 'Bạn đã hết lượt sử dụng mã khuyến mãi này rồi!'

    return True, ''


def update_availability(user, promotion, user_promotion_usage=None, increment_usage=True):
    step = 1 if increment_usage else -1

    if not increment_usage or promotion.availability_count > 0:
        promotion.availability_count -= step

    if user_promotion_usage:
        user_promotion_usage.usage_count += step
    elif increment_usage:
        create_user_promotion_usage(user.id, promotion.id)

    db.session.commit()

def validate_dates(form, field):
    if form.start_date.data and field.data:
        if field.data <= form.start_date.data:
            raise ValidationError('Ngày hết hạn phải sau ngày bắt đầu.')
        
def validate_promotion_value(form, field):
    value = field.data
    if value is None or value <= 0:
        raise ValidationError('Value must be greater than 0.')
    if is_coupon(form.promotion_type.data) and value > 0.5:
        raise ValidationError('For COUPON type, value must be at most 0.5.')
    
def validate_max_discount_amount(form, field):
    value = field.data
    if is_coupon(form.promotion_type.data) and (value is None or value <= 0):
        raise ValidationError('Max discount amount is required for COUPON type.')
    if value is not None and value < 0:
        raise ValidationError('Max discount amount must be non-negative.')

def validate_phone_number(form, field):
    phone_number = field.data.strip()
    if not phone_number.isdigit() or len(phone_number) < 10:
        raise ValidationError('Số điện thoại không hợp lệ. Vui lòng nhập số điện thoại từ 10 chữ số và chỉ chứa chữ số.')
    
def validate_password(form, field):
    password = (field.data or '').strip()
    special_chars = set('!@#$%^&*()_+-=[]{}|;:,.<>?/')

    checks = [
        (len(password) >= 8, 'Mật khẩu phải có ít nhất 8 ký tự.'),
        (any(char.isdigit() for char in password), 'Mật khẩu phải chứa ít nhất một chữ số.'),
        (any(char.isupper() for char in password), 'Mật khẩu phải chứa ít nhất một chữ hoa.'),
        (any(char.islower() for char in password), 'Mật khẩu phải chứa ít nhất một chữ thường.'),
        (
            any(char in special_chars for char in password),
            'Mật khẩu phải chứa ít nhất một ký tự đặc biệt (!@#$%^&*()_+-=[]{}|;:,.<>?/).'
        )
    ]

    for is_valid, error_message in checks:
        if not is_valid:
            raise ValidationError(error_message)
        
def is_existing_order_using_promotion(promotion):
    return Order.query.filter(Order.promotion_id == promotion.id, Order.status == 'PENDING').first() is not None
    