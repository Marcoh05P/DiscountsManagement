from datetime import datetime, timedelta

import pytest

from DiscountsManagementApp.dao import get_promotion_by_code, get_user_promotion_usage
from DiscountsManagementApp.validators.base import is_coupon, validate_date_range, validate_max_discount_amount, validate_order_data, validate_order_update, validate_password_value, validate_phone_number, validate_promotion_value, validate_registration_data
from DiscountsManagementApp.test.test_base import sample_promotion, test_app, test_session, sample_user_promotion_usage, sample_user, sample_order


@pytest.mark.parametrize("value, expected", [
    ("COUPON", True),
    ("VOUCHER", False),
    ("", False),
    (None, False),
])
def test_is_coupon(value, expected):
    assert is_coupon(value) == expected


@pytest.mark.parametrize("password, expected, error_message", [
    ("", False, 'Mật khẩu là bắt buộc!'),
    ("abc@123", False, 'Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường, chữ số và ký tự đặc biệt.'),
    ("abcdefgh", False, 'Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường, chữ số và ký tự đặc biệt.'),
    ("abcdEFGH", False, 'Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường, chữ số và ký tự đặc biệt.'),
    ("Abc@123", False, 'Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường, chữ số và ký tự đặc biệt.'),
    ("Abcd@1234", True, ''),
])
def test_validate_password_value(password, expected, error_message):
    is_valid, error = validate_password_value(password)
    assert is_valid == expected
    assert error == error_message


@pytest.mark.parametrize("full_name, phone_number, password, confirm, expected, error_message", [
    ("", "0123456789", "Abcd@1234", "Abcd@1234", False, 'Họ và tên là bắt buộc!'),
    ("ABC", "0123456789", "Abcd@1234", "Abcd@1234", True, ''),
    ("ABC", "0123456789", "Abcd@1234", "Abcd@12345",
     False, 'Mật khẩu xác nhận không khớp!'),
    ("ABC", "0123456789", "Abcd@12345", "Abcd@12345",
     True, ''),
])
def test_validate_registration_data(full_name, phone_number, password, confirm, expected, error_message):
    is_valid, error = validate_registration_data(
        full_name, phone_number, password, confirm)
    assert is_valid == expected
    assert error == error_message


@pytest.mark.parametrize("sub_total_amount, promotion_code, user_id, is_using_promotion, discount_amount, expected, error_message", [
    (None, "", None, False, None, False, 'Giá trị đơn hàng không hợp lệ!'),
    (100, "", None, True, None, False, 'Mã khuyến mãi không tồn tại!'),
    (100, "APPONLY8", None, True, None, False, 'Mã khuyến mãi chưa bắt đầu!'),
    (100, "SUMMER18", None, True, None, False,
     'Mã khuyến mãi đã hết hạn!'),
    (100, "LESS100K", None, True, None, False,
          'Mã khuyến mãi đã hết lượt sử dụng!'),
    (100, "MORNING12", None, True, None, False,
     'Giá trị đơn hàng phải lớn hơn hoặc bằng 250000.0 để áp dụng!'),
    (100, "SHIP50K", None, True, 50000, False,
     'Không thể sử dụng mã khuyến mãi này vì giá trị giảm giá vượt quá 50% giá trị đơn hàng!'),
    (100, "NEW10", 1, True, None, False,
     'Bạn đã hết lượt sử dụng mã khuyến mãi này rồi!'),
    (100, "NEW10", 2, False, None, True, ''),
])
def test_validate_order_data(sub_total_amount, promotion_code, user_id, is_using_promotion, discount_amount, expected, error_message, test_session, sample_user, sample_promotion, sample_user_promotion_usage):
    promotion = get_promotion_by_code(promotion_code)
    promotion_usage = None
    if user_id is not None and promotion:
        promotion_usage = get_user_promotion_usage(user_id, promotion.id)
    is_valid, error = validate_order_data(
        sub_total_amount=sub_total_amount, promotion=promotion, promotion_usage=promotion_usage, is_using_promotion=is_using_promotion, discount_amount=discount_amount)
    assert is_valid == expected
    assert error == error_message


def test_validate_date_range():
    now = datetime.now()
    assert validate_date_range(now, now + timedelta(days=1)) == (True, '')
    assert validate_date_range(now, now) == (
        False, 'Ngày hết hạn phải sau ngày bắt đầu.')
    assert validate_date_range(
        now + timedelta(days=1), now) == (False, 'Ngày hết hạn phải sau ngày bắt đầu.')


@pytest.mark.parametrize("value, promotion_type, expected, error_message", [
    (None, 'COUPON', False, 'Giá trị khuyến mãi phải lớn hơn 0.'),
    (-10, 'COUPON', False, 'Giá trị khuyến mãi phải lớn hơn 0.'),
    (0, 'COUPON', False, 'Giá trị khuyến mãi phải lớn hơn 0.'),
    (0.6, 'COUPON', False,
     'Đối với loại COUPON, giá trị khuyến mãi phải nhỏ hơn hoặc bằng 0.5.'),
    (0.5, 'COUPON', True, ''),
    (999, 'VOUCHER', False,
     'Đối với loại VOUCHER, giá trị khuyến mãi phải lớn hơn hoặc bằng 1000.'),
    (1000, 'VOUCHER', True, ''),

])
def test_validate_promotion_value(value, promotion_type, expected, error_message):
    is_valid, error = validate_promotion_value(value, promotion_type)
    assert is_valid == expected
    assert error == error_message


@pytest.mark.parametrize("max_discount_value, promotion_type, min_order_value, promotion_value, expected, error_message", [
    (None, 'COUPON', None, None, False,
     'Số tiền giảm giá tối đa phải lớn hơn 0 cho loại COUPON.'),
    (0, 'COUPON', None, None, False,
     'Số tiền giảm giá tối đa phải lớn hơn 0 cho loại COUPON.'),
    (1, 'COUPON', None, None, True, ''),
    (99, 'COUPON', 1000, 0.1, False,
     'Số tiền giảm giá tối đa phải ít nhất bằng số tiền giảm giá được tính từ giá trị đơn hàng tối thiểu và giá trị khuyến mãi cho loại COUPON.'),
    (100, 'COUPON', 1000, 0.1, True, ''),
    (None, 'VOUCHER', None, None, True, ''),
    (10, 'VOUCHER', None, None, False,
     'Số tiền giảm giá tối đa phải là 0 cho loại VOUCHER.'),
    (0, 'VOUCHER', None, None, True, ''),
])
def test_validate_max_discount_amount(max_discount_value, promotion_type, min_order_value, promotion_value, expected, error_message):
    is_valid, error = validate_max_discount_amount(
        max_discount_value, promotion_type, min_order_value, promotion_value)
    assert is_valid == expected
    assert error == error_message


@pytest.mark.parametrize("phone_number, expected, error_message", [
    ("", False, 'Số điện thoại là bắt buộc!'),
    ("1234567890", True, ''),
    ("123456789", False, 'Số điện thoại không hợp lệ. Vui lòng nhập số điện thoại từ 10 chữ số và chỉ chứa chữ số.'),
    ("ABCJhdfsgsdsdhb", False, 'Số điện thoại không hợp lệ. Vui lòng nhập số điện thoại từ 10 chữ số và chỉ chứa chữ số.'),
])  
def test_validate_phone_number(phone_number, expected, error_message):
    is_valid, error = validate_phone_number(phone_number)
    assert is_valid == expected
    assert error == error_message


@pytest.mark.parametrize("customer_id, old_status, new_status, current_user_idx, expected, error_message", [
    (2, 'PENDING', 'COMPLETED', 2, False, 'Bạn không có quyền cập nhật đơn hàng này.'),
    (1, 'PENDING', 'PENDING', 0, True, ''),
    (1, 'PENDING', 'COMPLETED', 0, True, ''),
    (1, 'PENDING', 'CANCELLED', 0, True, ''),
    (1, 'PENDING', 'djfshjdshjsdhk', 0, False, 'Trạng thái cập nhật không hợp lệ.'),
    (1, 'COMPLETED', 'PENDING', 0, False, 'Chỉ có thể cập nhật đơn hàng ở trạng thái đang chờ xử lý.'),
    (1, 'CANCELLED', 'PENDING', 0, False, 'Chỉ có thể cập nhật đơn hàng ở trạng thái đang chờ xử lý.'),
    # Test ADMIN có index 3
    (1, 'PENDING', 'COMPLETED', 3, True, ''),
])
def test_validate_order_update(customer_id, old_status, new_status, current_user_idx, expected, error_message, test_session, sample_user, mocker):
    mocker.patch('flask_login.utils._get_user', return_value=sample_user[current_user_idx])
    is_valid, error = validate_order_update(customer_id, old_status, new_status)
    assert is_valid == expected
    assert error == error_message