from datetime import datetime
from DiscountsManagementApp.models import UserRole
from DiscountsManagementApp.test.test_base import FakeUser, test_app, test_client, test_session, sample_user, sample_promotion, sample_order, sample_user_promotion_usage, time_freezer
import pytest


@pytest.mark.parametrize("code, amount, ptype, page, expected_status_code, expected_page, expected_total_pages, expected_has_next, expected_has_prev, expected_items_count, error_message", [
    (None, None, None, None, 200, 1, 3, True, False, 3, None),
    (None, None, None, 2, 200, 2, 3, True, True, 3, None),
    (None, None, None, 3, 200, 3, 3, False, True, 2, None),
    ('LESS', None, None, None, 200, 1, 1, False, False, 1, None),
    (None, 100000, None, None, 200, 1, 1, False, False, 3, None),
    (None, None, 'VOUCHER', None, 200, 1, 2, True, False, 3, None),
    ('LESS', '1000000', 'VOUCHER', None, 200, 1, 1, False, False, 1, None),
    ('dsaghuisdauisd', None, None, None, 200, 1, 0, False, False, 0, None),
    (None, -1, None, None, 400, 1, 0, False,
     False, 0, 'Giá trị đơn hàng không hợp lệ!'),
    (None, 'abc', None, None, 400, 1, 0, False,
     False, 0, 'Giá trị đơn hàng không hợp lệ!'),
    (None, None, None, 0, 400, 1, 0, False, False, 0, 'Số trang không hợp lệ!'),
    (None, None, None, 'abc', 400, 1, 0, False, False, 0, 'Số trang không hợp lệ!'),

])

def test_get_promotion(test_client, sample_promotion, sample_user_promotion_usage, code, amount, ptype, page, expected_status_code, expected_page, expected_total_pages, expected_has_next, expected_has_prev, expected_items_count, error_message):
    res = test_client.get('api/promotions', query_string={
        'code': code,
        'amount': amount,
        'ptype': ptype,
        'page': page
    })
    assert res.status_code == expected_status_code
    if res.status_code == 200:
        data = res.get_json()
        assert data['page'] == expected_page
        assert data['total_pages'] == expected_total_pages
        assert data['has_next'] == expected_has_next
        assert data['has_prev'] == expected_has_prev
        assert len(data['items']) == expected_items_count

        if code:
            assert all(code in item['code'] for item in data['items'])

        if amount:
            assert all(item['min_order_value'] <= float(amount)
                       for item in data['items'])

        if ptype:
            assert all(item['promotion_type'] ==
                       ptype for item in data['items'])
    elif res.status_code == 400:
        data = res.get_json()
        assert data['error'] == error_message
        
#TODO: Test nghiệp vụ tạo promotion


@pytest.mark.parametrize("user_id, user_role, expected_status_code, error_message, code, promotion_type, value, availability_count, start_date, expire_date, max_discount_amount, min_order_value, description", [
    (4, UserRole.ADMIN, 201, None, 'TESTCODE', 'VOUCHER', 10000, 100, '2026-01-01 00:00:00', '2026-12-31 23:59:59', 0, 50000, 'Mã khuyến mãi test'),
    (5, UserRole.CUSTOMER, 302, None, 'TESTCODE', 'VOUCHER', 10000, 100, '2026-01-01 00:00:00', '2026-12-31 23:59:59', 0, 50000, 'Mã khuyến mãi test'),
    (4, UserRole.ADMIN, 400, 'Mã khuyến mãi là bắt buộc!', '', 'VOUCHER', 10000, 100, '2026-01-01 00:00:00', '2026-12-31 23:59:59', 0, 50000, 'Mã khuyến mãi test'),
    (4, UserRole.ADMIN, 400, 'Giá trị khuyến mãi phải lớn hơn 0.', 'TESTCODE', 'VOUCHER', -10000, 100, '2026-01-01 00:00:00', '2026-12-31 23:59:59', 0, 50000, 'Mã khuyến mãi test'),
    (4, UserRole.ADMIN, 400, 'Số lượng sử dụng phải là một số nguyên dương hoặc bằng 0!', 'TESTCODE', 'VOUCHER', 10000, -1, '2026-01-01 00:00:00', '2026-12-31 23:59:59', 0, 50000, 'Mã khuyến mãi test'),
    (4, UserRole.ADMIN, 400, 'Ngày hết hạn phải sau ngày bắt đầu.', 'TESTCODE', 'VOUCHER', 10000, 100, '2026-12-31 23:59:59', '2026-01-01 00:00:00', 0, 50000, 'Mã khuyến mãi test'),
    

])

def test_create_promotion(test_client, mocker, sample_user, user_id, user_role, expected_status_code, error_message, code, promotion_type, value, availability_count, start_date, expire_date, max_discount_amount, min_order_value, description):
    fakeUser = FakeUser(is_authenticated=True, user_id=user_id, role=user_role)
    mocker.patch("flask_login.utils._get_user", return_value=fakeUser)

    res = test_client.post('api/promotions', data={
        'code': code,
        'promotion_type': promotion_type,
        'value': value,
        'availability_count': availability_count,
        'start_date': start_date,
        'expire_date': expire_date,
        'max_discount_amount': max_discount_amount,
        'min_order_value': min_order_value,
        'description': description
    })
    
    assert res.status_code == expected_status_code
    if res.status_code == 201:
        data = res.get_json()

        if code:
            assert data['code'] == code
        if promotion_type:
            assert data['promotion_type'] == promotion_type
        if value:
            assert data['value'] == value
        if availability_count is not None:
            assert data['availability_count'] == availability_count
        if start_date:
            assert data['start_date'].replace('T', ' ') == start_date
        if expire_date:
            assert data['expire_date'].replace('T', ' ') == expire_date
        if max_discount_amount is not None:
            assert data['max_discount_amount'] == max_discount_amount
        if min_order_value is not None:
            assert data['min_order_value'] == min_order_value
        if description:
            assert data['description'] == description
        
    elif res.status_code == 400:
        data = res.get_json()
        assert data['error'] == error_message
    
    
