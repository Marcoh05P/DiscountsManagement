import hashlib

import pytest

from DiscountsManagementApp.dao import get_user_by_phone_number
from DiscountsManagementApp.test.test_base import test_app, test_client, test_session, sample_user


@pytest.mark.parametrize("phone_number, full_name, password, confirm, expected_status_code, expected_user_id, expected_role, error_message", [
    # Mặc định database đã có sẵn 4 user, nên id của user mới sẽ là 5

    ("55465645645", "abc", "Password@123",
     "Password@123", 302, 5, "CUSTOMER", ''),
    ("55465645645", "   ", "Password@123", "Password@123",
     200, 5, "CUSTOMER", 'Họ và tên là bắt buộc!'),
    (None, "abc", "Password@123", "Password@123",
     200, 5, "CUSTOMER", 'Số điện thoại là bắt buộc!'),
    ('345hg34h', "abc", "Password@123", "Password@123", 200, 5, "CUSTOMER",
     'Số điện thoại không hợp lệ. Vui lòng nhập số điện thoại từ 10 chữ số và chỉ chứa chữ số.'),
    ('4343', "abc", "Password@123", "Password@123", 200, 5, "CUSTOMER",
     'Số điện thoại không hợp lệ. Vui lòng nhập số điện thoại từ 10 chữ số và chỉ chứa chữ số.'),
    ("55465645645", "abc", None, "Password@123",
     200, 5, "CUSTOMER", 'Mật khẩu là bắt buộc!'),
    ("55465645645", "abc", 'abc', "Password@123",
     200, 5, "CUSTOMER", 'Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường, chữ số và ký tự đặc biệt.'),
    ("55465645645", "abc", "Password@123",
     "Password@1234", 200, 5, "CUSTOMER", 'Mật khẩu xác nhận không khớp!'),

])
def test_register_user(test_client, test_session, sample_user, phone_number, full_name, password, confirm, expected_status_code, expected_user_id, expected_role, error_message):
    res = test_client.post('/register', data={
        'phone_number': phone_number,
        'full_name': full_name,
        'password': password,
        'confirm': confirm
    })
    assert res.status_code == expected_status_code

    if expected_status_code == 302:
        user = get_user_by_phone_number(phone_number)
        password_hash = str(hashlib.md5(
            password.strip().encode('utf-8')).hexdigest())
        assert user is not None
        assert user.id == expected_user_id
        assert user.full_name == full_name
        assert user.password_hash == password_hash
        assert user.role.value == expected_role
    else:
        assert error_message.encode('utf-8') in res.data
