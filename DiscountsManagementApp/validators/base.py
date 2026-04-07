import re
from datetime import datetime

from DiscountsManagementApp.models import PromotionType


def is_coupon(value):
    if isinstance(value, PromotionType):
        return value == PromotionType.COUPON
    return str(value) == PromotionType.COUPON.value


def validate_password_value(password):
    if not password:
        return False, 'Mật khẩu là bắt buộc!'

    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{}|;:,.<>?/]).{8,}$"
    if not re.match(pattern, password):
        return False, 'Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường, chữ số và ký tự đặc biệt.'

    return True, ''


def validate_registration_data(full_name, phone_number, password, confirm):
    if not full_name or not full_name.strip():
        return False, 'Họ và tên là bắt buộc!'
    is_phone_valid, phone_error = validate_phone_number(phone_number)
    if not is_phone_valid:
        return False, phone_error
    is_password_valid, password_error = validate_password_value(password)
    if not is_password_valid:
        return False, password_error
    if password != confirm:
        return False, 'Mật khẩu xác nhận không khớp!'
    return True, ''


def validate_order_data(user, sub_total_amount=None, promotion=None, promotion_usage=None, is_using_promotion=False,
                        discount_amount=None):
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


def validate_date_range(start_date, expire_date):
    if start_date and expire_date and expire_date <= start_date:
        return False, 'Ngày hết hạn phải sau ngày bắt đầu.'
    return True, ''


def validate_promotion_value(value, promotion_type):
    if value is None or value <= 0:
        return False, 'Giá trị khuyến mãi phải lớn hơn 0.'
    if is_coupon(promotion_type) and value > 0.5:
        return False, 'Đối với loại COUPON, giá trị khuyến mãi phải nhỏ hơn hoặc bằng 0.5.'
    elif not is_coupon(promotion_type) and value < 1000:
        return False, 'Đối với loại VOUCHER, giá trị khuyến mãi phải lớn hơn hoặc bằng 1000.'
    return True, ''


def validate_max_discount_amount(max_discount_value, promotion_type, min_order_value=None, promotion_value=None):
    if is_coupon(promotion_type):
        if max_discount_value is None or max_discount_value <= 0:
            return False, 'Số tiền giảm giá tối đa phải lớn hơn 0 cho loại COUPON.'
        elif min_order_value and promotion_value and max_discount_value < (min_order_value * promotion_value):
            return False, 'Số tiền giảm giá tối đa phải ít nhất bằng số tiền giảm giá được tính từ giá trị đơn hàng tối thiểu và giá trị khuyến mãi cho loại COUPON.'
    else:
        if max_discount_value is not None and max_discount_value != 0:
            return False, 'Số tiền giảm giá tối đa phải là 0 cho loại VOUCHER.'
    return True, ''


def validate_phone_number(phone_number):
    if not phone_number:
        return False, 'Số điện thoại là bắt buộc!'
    phone_number = phone_number.strip()
    if not phone_number.isdigit() or len(phone_number) < 10:
        return False, 'Số điện thoại không hợp lệ. Vui lòng nhập số điện thoại từ 10 chữ số và chỉ chứa chữ số.'
    return True, ''
