from datetime import datetime
from DiscountsManagementApp.dao import get_promotion_by_code
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


@pytest.mark.parametrize("user_id, user_role, code, promotion_type, value, availability_count, start_date, expire_date, max_discount_amount, min_order_value, description, expected_status_code, expected_id, expected_max_discount_amount, expected_min_order_value, expected_remaining_availability_count, error_message", [
    # Mặc định database đã có sẵn 20 promotion, nên id của order mới sẽ là 21

    # Thành công với ADMIN
    (4, UserRole.ADMIN, 'NEWCODE', 'COUPON', 0.2, 100, '2026-01-01 00:00:00',
     '2026-12-31 23:59:59', 20000, 40000, 'Test description', 201, 21, 20000, 40000, 100, None),
    (4, UserRole.ADMIN, 'NEWCODE', 'VOUCHER', 20000, 100, '2026-01-01 00:00:00',
     '2026-12-31 23:59:59', None, None, 'Test description', 201, 21, None, 0, 100, None),

    # Thất bại do không chưa đăng nhập
    (None, None, 'NEWCODE', 'COUPON', 0.2, 100, '2026-01-01 00:00:00',
     '2026-12-31 23:59:59', 20000, 40000, 'Test description', 403, None, None, None, None, None),

])
def test_create_promotion(test_client, mocker, sample_user, sample_promotion, user_id, user_role, code, promotion_type, value, availability_count, start_date, expire_date, max_discount_amount, min_order_value, description, expected_status_code, expected_id, expected_max_discount_amount, expected_min_order_value, expected_remaining_availability_count, error_message):
    fakeUser = FakeUser(
        is_authenticated=False if user_id is None else True, user_id=user_id, role=user_role)
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
        promotion = get_promotion_by_code(code)
        assert promotion is not None
        assert promotion.id == expected_id == data['id']
        assert promotion.code == code == data['code']
        assert promotion.promotion_type.value == promotion_type == data['promotion_type']
        assert promotion.value == value == data['value']
        assert promotion.availability_count == availability_count == data['availability_count']
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        expire_date_obj = datetime.strptime(expire_date, "%Y-%m-%d %H:%M:%S")
        assert promotion.start_date == start_date_obj == datetime.fromisoformat(
            data['start_date'])
        assert promotion.expire_date == expire_date_obj == datetime.fromisoformat(
            data['expire_date'])
        assert promotion.max_discount_amount == data['max_discount_amount'] == expected_max_discount_amount
        assert promotion.min_order_value == data['min_order_value'] == expected_min_order_value
        assert promotion.description == description == (None if data['description'] == 'null' else data['description'])
        assert promotion.remaining_availability_count == expected_remaining_availability_count == data['remaining_availability_count']

    elif res.status_code == 400:
        data = res.get_json()
        assert data['error'] == error_message
