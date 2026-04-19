import hashlib
from datetime import datetime
from flask import current_app
import pytest

from DiscountsManagementApp.dao import add_user, auth_user, create_order, get_promotion_by_code, get_promotions, get_user_by_phone_number, update_order
from DiscountsManagementApp.test.test_base import test_app, test_session, sample_user, sample_promotion, sample_order, sample_user_promotion_usage


def test_get_user_by_phone_number_success(test_session, sample_user):
    user = get_user_by_phone_number(phone_number='123456789')
    password_hash = hashlib.md5('password123'.encode("utf-8")).hexdigest()
    assert user is not None
    assert user.full_name == 'Nguyen Van A'
    assert user.phone_number == '123456789'
    assert user.role.name == 'CUSTOMER'
    assert user.password_hash == password_hash


def test_get_user_by_phone_number_not_found(test_session, sample_user):
    user = get_user_by_phone_number(phone_number='000000000')
    assert user is None


def test_auth_user_success(test_session, sample_user):
    user = auth_user(phone_number='123456789', password='password123')
    assert user is not None
    assert user.full_name == 'Nguyen Van A'
    assert user.phone_number == '123456789'
    assert user.role.name == 'CUSTOMER'


def test_auth_user_wrong_password(test_session, sample_user):
    user = auth_user(phone_number='123456789', password='wrongpassword')
    assert user is None


def test_auth_user_nonexistent_phone(test_session, sample_user):
    user = auth_user(phone_number='000000000', password='password123')
    assert user is None


def test_add_user_success(test_session, sample_user):
    user = add_user(phone_number='1111111',
                    password='12345', full_name='Nahhsdja')
    assert user is not None
    assert user.full_name == 'Nahhsdja'
    assert user.phone_number == '1111111'
    assert user.role.name == 'CUSTOMER'
    assert user.password_hash == hashlib.md5(
        '12345'.encode("utf-8")).hexdigest()


def test_add_user_duplicate_phone(test_session, sample_user):
    with pytest.raises(Exception):
        add_user(phone_number='123456789',
                 password='12345', full_name='Nahhsdja')


def test_create_order_success(test_session, sample_user, sample_promotion):
    user = sample_user[0]
    promotion = sample_promotion[0]
    order = create_order(customer_id=user.id,
                         sub_total_amount=500000,
                         discount_amount=100000,
                         final_amount=400000,
                         promotion_id=promotion.id)
    assert order is not None
    assert order.customer_id == user.id
    assert order.sub_total_amount == 500000
    assert order.discount_amount == 100000
    assert order.final_amount == 400000
    assert order.promotion_id == promotion.id


def test_create_order_without_promotion(test_session, sample_user):
    user = sample_user[0]
    order = create_order(customer_id=user.id,
                         sub_total_amount=500000,
                         discount_amount=0,
                         final_amount=500000)
    assert order is not None
    assert order.customer_id == user.id
    assert order.sub_total_amount == 500000
    assert order.discount_amount == 0
    assert order.final_amount == 500000
    assert order.promotion_id is None


def test_create_order_without_user(test_session, sample_promotion):
    promotion = sample_promotion[0]
    with pytest.raises(Exception):
        create_order(sub_total_amount=500000,
                     discount_amount=100000,
                     final_amount=400000,
                     promotion_id=promotion.id)


def test_update_order_status_success(test_session, sample_user, sample_promotion):
    user = sample_user[0]
    promotion = sample_promotion[0]
    order = create_order(customer_id=user.id,
                         sub_total_amount=500000,
                         discount_amount=100000,
                         final_amount=400000,
                         promotion_id=promotion.id)
    updated_order = update_order(order_id=order.id, status='COMPLETED')
    assert updated_order is not None
    assert updated_order.status.name == 'COMPLETED'


def test_update_order_status_invalid_order(test_session):
    updated_order = update_order(order_id=0, status='COMPLETED')
    assert updated_order is None


def test_get_promotion_by_code_success(test_session, sample_promotion):
    promotion = get_promotion_by_code(code='NEW10')
    assert promotion is not None
    assert promotion.code == 'NEW10'
    assert promotion.promotion_type.name == 'COUPON'
    assert promotion.availability_count == 150
    assert promotion.value == 0.10
    assert promotion.max_discount_amount == 100000
    assert promotion.min_order_value == 0
    assert promotion.description == 'Giam 10% cho khach hang moi'
    assert promotion.start_date == datetime(2026, 3, 1, 0, 0, 0)
    assert promotion.expire_date == datetime(2026, 12, 31, 23, 59, 59)


def test_get_promotion_by_code_not_found(test_session):
    promotion = get_promotion_by_code(code='BRUH')
    assert promotion is None


@pytest.mark.parametrize("code, expired, ptype, order_value, is_available, page, expected_page, expected_pages, expected_total, expected_count", [
    (None, False, None, None, True, 1, 1, 3, 8, 3),
    ("LESS", False, None, None, True, 1, 1, 1, 1, 1),
    (None, True, None, None, True, 1, 1, 1, 2, 2),
    (None, False, "VOUCHER", None, True, 1, 1, 2, 4, 3),
    (None, False, None, 100000, True, 1, 1, 1, 3, 3),
    (None, False, None, None, False, 1, 1, 4, 12, 3),
    (None, False, "COUPON", 300000, True, 1, 1, 1, 3, 3),
    (None, False, "VOUCHER", 400000, False, 1, 1, 1, 3, 3),
    (None, False, "VOUCHER", 400000, True, 1, 1, 1, 2, 2),
    (None, True, "VOUCHER", None, True, 1, 1, 1, 1, 1),
    (None, True, "VOUCHER", None, False, 1, 1, 1, 2, 2),
    ("LESS", False, "VOUCHER", None, False, 1, 1, 1, 3, 3),
    ("LESS", False, "VOUCHER", 600000, False, 1, 1, 1, 2, 2),
    ("LESS", False, "VOUCHER", 600000, True, 1, 1, 0, 0, 0),
    (None, False, None, None, True, 3, 3, 3, 8, 2),
    (None, False, None, None, False, 2, 2, 4, 12, 3),
    (None, False, None, 0, True, 1, 1, 3, 8, 3),
    (None, False, None, -1, True, 1, 1, 3, 8, 3),
    (None, None, "YHDGSYJSYJAF", None, True, 1, 1, 0, 0, 0),
    (None, False, None, None, None, 1, 1, 4, 12, 3),
    (None, False, None, None, True, 0, 1, 3, 8, 3),
    (None, False, None, None, True, -5, 1, 3, 8, 3),
    (None, False, None, None, True, None, 1, 3, 8, 3),
    (None, False, None, None, True, "sdfdfssfddfs", 1, 3, 8, 3)
])
def test_get_promotions(test_session, sample_promotion, sample_user_promotion_usage, code, expired, ptype, order_value, is_available, page, expected_page, expected_pages, expected_total, expected_count):
    promotions = get_promotions(code=code, expired=expired, ptype=ptype,
                                order_value=order_value, is_available=is_available, page=page)
    assert promotions.pages == expected_pages
    assert promotions.page == expected_page
    assert promotions.total == expected_total
    assert len(promotions.items) == expected_count


def test_get_promotions_with_code(test_session, sample_promotion, sample_user_promotion_usage):
    promotions = get_promotions(code='LESS')
    assert promotions.pages == 1
    assert promotions.page == 1
    assert promotions.total == 1
    assert len(promotions.items) == 1
    assert all('LESS' in p.code for p in promotions.items)


def test_get_promotions_with_expired(test_session, sample_promotion, sample_user_promotion_usage):
    promotions = get_promotions(expired=True)
    assert promotions.pages == 1
    assert promotions.page == 1
    assert promotions.total == 2
    assert len(promotions.items) == 2
    assert all(p.expire_date < datetime.now() for p in promotions.items)


def test_get_promotions_with_ptype(test_session, sample_promotion, sample_user_promotion_usage):
    promotions = get_promotions(ptype='VOUCHER')
    assert promotions.pages == 2
    assert promotions.page == 1
    assert promotions.total == 4
    assert len(promotions.items) == 3
    assert all(p.promotion_type.name == 'VOUCHER' for p in promotions.items)


def test_get_promotions_with_order_value(test_session, sample_promotion, sample_user_promotion_usage):
    promotions = get_promotions(order_value=100000)
    assert promotions.pages == 1
    assert promotions.page == 1
    assert promotions.total == 3
    assert len(promotions.items) == 3
    assert all(p.min_order_value <= 100000 for p in promotions.items)


def test_get_promotions_include_not_available(test_session, sample_promotion, sample_user_promotion_usage):
    promotions = get_promotions(is_available=False)
    assert promotions.pages == 4
    assert promotions.page == 1
    assert promotions.total == 12
    assert len(promotions.items) == 3
    assert any(p.remaining_availability_count == 0 for p in promotions.items)

