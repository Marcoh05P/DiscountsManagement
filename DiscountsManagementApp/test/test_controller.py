from datetime import datetime

from DiscountsManagementApp.models import Order, OrderStatus, Promotion, PromotionType, UserRole
from DiscountsManagementApp.test.test_base import FakeUser, test_app, test_client


class FakePaginationResult:
    def __init__(self, page, pages, has_next, has_prev, items):
        self.page = page
        self.pages = pages
        self.has_next = has_next
        self.has_prev = has_prev
        self.items = items


ORDER = Order(
    id=1,
    customer_id=1,
    created_date=datetime(2026, 5, 19, 10, 0, 0),
    sub_total_amount=100.0,
    discount_amount=10.0,
    final_amount=90.0,
    promotion_id=1,
    status=OrderStatus.PENDING
)

PROMOTION = Promotion(
    id=1,
    code='TEST',
    start_date=datetime(2026, 3, 1, 0, 0, 0),
    expire_date=datetime(2026, 12, 31, 23, 59, 59),
    promotion_type=PromotionType.COUPON,
    availability_count=150,
    value=0.10,
    max_discount_amount=100000,
    min_order_value=0,
    description='test'
)


def test_login_success(test_client, mocker):

    auth_user_mock = mocker.patch(
        'DiscountsManagementApp.index.dao.auth_user', return_value=FakeUser(is_authenticated=True))

    mocker.patch('DiscountsManagementApp.index.login_user')

    res = test_client.post('/login', data={
        'phone_number': 'test',
        'password': 'test'
    })

    assert res.status_code == 302
    auth_user_mock.assert_called_once_with('test', 'test')


def test_login_failure(test_client, mocker):

    auth_user_mock = mocker.patch(
        'DiscountsManagementApp.index.dao.auth_user', return_value=None)

    res = test_client.post('/login', data={
        'phone_number': 'test',
        'password': 'test'
    })

    assert res.status_code == 200
    assert 'Số điện thoại hoặc mật khẩu không đúng'.encode('utf-8') in res.data
    auth_user_mock.assert_called_once_with('test', 'test')


def test_login_exception(test_client, mocker):

    auth_user_mock = mocker.patch(
        'DiscountsManagementApp.index.dao.auth_user', side_effect=Exception('Database error'))

    res = test_client.post('/login', data={
        'phone_number': 'test',
        'password': 'test'
    })

    assert res.status_code == 200
    assert 'Database error'.encode('utf-8') in res.data
    auth_user_mock.assert_called_once_with('test', 'test')


def test_register_success(test_client, mocker):

    validate_registration_data_mock = mocker.patch(
        'DiscountsManagementApp.index.validate_registration_data', return_value=(True, ''))
    check_phone_number_exists_mock = mocker.patch(
        'DiscountsManagementApp.index.check_phone_number_exists', return_value=False)
    add_user_mock = mocker.patch('DiscountsManagementApp.index.dao.add_user')
    auth_user_mock = mocker.patch(
        'DiscountsManagementApp.index.dao.auth_user', return_value=FakeUser(is_authenticated=True))
    mocker.patch('DiscountsManagementApp.index.login_user')

    res = test_client.post('/register', data={
        'phone_number': 'test',
        'full_name': 'test',
        'password': 'test',
        'confirm': 'test'
    })

    assert res.status_code == 302
    validate_registration_data_mock.assert_called_once_with(
        'test', 'test', 'test', 'test')
    check_phone_number_exists_mock.assert_called_once_with('test')
    add_user_mock.assert_called_once_with(
        phone_number='test', password='test', full_name='test')
    auth_user_mock.assert_called_once_with('test', 'test')


def test_register_validation_bad_data(test_client, mocker):

    validate_registration_data_mock = mocker.patch(
        'DiscountsManagementApp.index.validate_registration_data', return_value=(False, 'error message test'))

    res = test_client.post('/register', data={
        'phone_number': 'test',
        'full_name': 'test',
        'password': 'test',
        'confirm': 'test'
    })

    assert res.status_code == 200
    assert 'error message test'.encode('utf-8') in res.data
    validate_registration_data_mock.assert_called_once_with(
        'test', 'test', 'test', 'test')


def test_register_phone_exists(test_client, mocker):

    validate_registration_data_mock = mocker.patch(
        'DiscountsManagementApp.index.validate_registration_data', return_value=(True, ''))
    check_phone_number_exists_mock = mocker.patch(
        'DiscountsManagementApp.index.check_phone_number_exists', return_value=True)

    res = test_client.post('/register', data={
        'phone_number': 'test',
        'full_name': 'test',
        'password': 'test',
        'confirm': 'test'
    })

    assert res.status_code == 200
    assert 'Số điện thoại đã được sử dụng'.encode('utf-8') in res.data
    validate_registration_data_mock.assert_called_once_with(
        'test', 'test', 'test', 'test')
    check_phone_number_exists_mock.assert_called_once_with('test')


def test_register_exception(test_client, mocker):
    validate_registration_data_mock = mocker.patch(
        'DiscountsManagementApp.index.validate_registration_data', return_value=(True, ''))
    check_phone_number_exists_mock = mocker.patch(
        'DiscountsManagementApp.index.check_phone_number_exists', return_value=False)
    add_user_mock = mocker.patch(
        'DiscountsManagementApp.index.dao.add_user', side_effect=Exception('Database error'))

    res = test_client.post('/register', data={
        'phone_number': 'test',
        'full_name': 'test',
        'password': 'test',
        'confirm': 'test'
    })

    assert res.status_code == 200
    assert 'Database error'.encode('utf-8') in res.data
    validate_registration_data_mock.assert_called_once_with(
        'test', 'test', 'test', 'test')
    check_phone_number_exists_mock.assert_called_once_with('test')
    add_user_mock.assert_called_once_with(
        phone_number='test', password='test', full_name='test')


def test_create_order_api_success_with_promotion(test_client, mocker):
    user = FakeUser(user_id=1, is_authenticated=True)
    mocker.patch('flask_login.utils._get_user', return_value=user)

    get_promotion_mock = mocker.patch('DiscountsManagementApp.index.get_promotion_by_code',
                                      return_value=PROMOTION)
    get_user_promotion_usage_mock = mocker.patch(
        'DiscountsManagementApp.index.dao.get_user_promotion_usage', return_value=None)
    validate_order_data_mock = mocker.patch('DiscountsManagementApp.index.validate_order_data',
                                            return_value=(True, ''))
    create_order_mock = mocker.patch(
        'DiscountsManagementApp.index.dao.create_order', return_value=ORDER)
    update_availability_mock = mocker.patch(
        'DiscountsManagementApp.index.update_availability')

    res = test_client.post('/api/orders', data={
        'promotion_code': 'TEST',
        'sub_total_amount': 100
    })

    assert res.status_code == 201
    assert res.get_json() == ORDER.to_dict()
    get_promotion_mock.assert_called_once_with('TEST')
    get_user_promotion_usage_mock.assert_called_once_with(1, 1)
    validate_order_data_mock.assert_called_once_with(
        sub_total_amount=100.0,
        promotion=PROMOTION,
        promotion_usage=None,
        is_using_promotion=True,
        discount_amount=10.0
    )
    create_order_mock.assert_called_once_with(
        customer_id=1, sub_total_amount=100.0, discount_amount=10, final_amount=90.0, promotion_id=1)
    update_availability_mock.assert_called_once_with(
        user, PROMOTION, user_promotion_usage=None, increment_usage=True)


def test_create_order_api_success_without_promotion(test_client, mocker):
    user = FakeUser(user_id=1, is_authenticated=True)
    mocker.patch('flask_login.utils._get_user', return_value=user)

    validate_order_data_mock = mocker.patch('DiscountsManagementApp.index.validate_order_data',
                                            return_value=(True, ''))

    create_order_mock = mocker.patch(
        'DiscountsManagementApp.index.dao.create_order', return_value=ORDER)

    res = test_client.post('/api/orders', data={
        'sub_total_amount': 100
    })

    assert res.status_code == 201
    assert res.get_json() == ORDER.to_dict()
    validate_order_data_mock.assert_called_once_with(
        sub_total_amount=100.0,
        promotion=None,
        promotion_usage=None,
        is_using_promotion=False,
        discount_amount=0.0
    )
    create_order_mock.assert_called_once_with(
        customer_id=1, sub_total_amount=100.0, discount_amount=0.0, final_amount=100.0, promotion_id=None)


def test_create_order_api_validation_bad_data(test_client, mocker):
    user = FakeUser(user_id=1, is_authenticated=True)
    mocker.patch('flask_login.utils._get_user', return_value=user)

    get_promotion_mock = mocker.patch('DiscountsManagementApp.index.get_promotion_by_code',
                                      return_value=PROMOTION)
    get_user_promotion_usage_mock = mocker.patch(
        'DiscountsManagementApp.index.dao.get_user_promotion_usage', return_value=None)
    validate_order_data_mock = mocker.patch('DiscountsManagementApp.index.validate_order_data',
                                            return_value=(False, 'error message test'))

    res = test_client.post('/api/orders', data={
        'promotion_code': 'TEST',
        'sub_total_amount': 100
    })

    assert res.status_code == 400
    data = res.get_json()
    assert 'error' in data
    assert data == {'error': 'error message test'}
    get_promotion_mock.assert_called_once_with('TEST')
    get_user_promotion_usage_mock.assert_called_once_with(1, 1)
    validate_order_data_mock.assert_called_once_with(
        sub_total_amount=100.0,
        promotion=PROMOTION,
        promotion_usage=None,
        is_using_promotion=True,
        discount_amount=10.0
    )


def test_create_order_api_exception(test_client, mocker):
    user = FakeUser(user_id=1, is_authenticated=True)

    mocker.patch('flask_login.utils._get_user', return_value=user)
    get_promotion_mock = mocker.patch('DiscountsManagementApp.index.get_promotion_by_code',
                                      return_value=PROMOTION)
    get_user_promotion_usage_mock = mocker.patch(
        'DiscountsManagementApp.index.dao.get_user_promotion_usage', return_value=None)
    validate_order_data_mock = mocker.patch('DiscountsManagementApp.index.validate_order_data',
                                            return_value=(True, ''))

    create_order_mock = mocker.patch(
        'DiscountsManagementApp.index.dao.create_order', side_effect=Exception('Database error'))

    res = test_client.post('/api/orders', data={
        'promotion_code': 'TEST',
        'sub_total_amount': 100
    })

    assert res.status_code == 400
    data = res.get_json()
    assert 'error' in data
    assert data == {
        'error': 'Không thể tạo đơn hàng do Database error'}
    get_promotion_mock.assert_called_once_with('TEST')
    get_user_promotion_usage_mock.assert_called_once_with(1, 1)
    validate_order_data_mock.assert_called_once_with(
        sub_total_amount=100.0,
        promotion=PROMOTION,
        promotion_usage=None,
        is_using_promotion=True,
        discount_amount=10.0
    )
    create_order_mock.assert_called_once_with(
        customer_id=1, sub_total_amount=100.0, discount_amount=10, final_amount=90.0, promotion_id=1)


def test_create_order_api_unauthenticated(test_client, mocker):
    mocker.patch('flask_login.utils._get_user',
                 return_value=FakeUser(is_authenticated=False))

    res = test_client.post('/api/orders', data={
        'promotion_code': 'TEST',
        'sub_total_amount': 100
    })

    assert res.status_code == 401
    assert b'Unauthorized' in res.data


def test_update_order_status_api_success_with_completion(test_client, mocker):
    user = FakeUser(user_id=1, is_authenticated=True)
    mocker.patch('flask_login.utils._get_user', return_value=user)

    get_order_mock = mocker.patch(
        'DiscountsManagementApp.index.get_order_by_id', return_value=ORDER)
    validate_order_update_mock = mocker.patch(
        'DiscountsManagementApp.index.validate_order_update', return_value=(True, ''))
    update_order_mock = mocker.patch(
        'DiscountsManagementApp.index.dao.update_order', return_value=ORDER)

    res = test_client.patch('/api/orders/1', data={
        'status': 'COMPLETED'
    })

    assert res.status_code == 204
    get_order_mock.assert_called_once_with(1)
    validate_order_update_mock.assert_called_once_with(
        customer_id=1, old_status='PENDING', new_status='COMPLETED')
    update_order_mock.assert_called_once_with(1, status='COMPLETED')


def test_update_order_status_api_success_with_cancellation(test_client, mocker):
    user = FakeUser(user_id=1, is_authenticated=True)
    mocker.patch('flask_login.utils._get_user', return_value=user)

    get_order_mock = mocker.patch(
        'DiscountsManagementApp.index.get_order_by_id', return_value=ORDER)
    validate_order_update_mock = mocker.patch(
        'DiscountsManagementApp.index.validate_order_update', return_value=(True, ''))
    update_order_mock = mocker.patch(
        'DiscountsManagementApp.index.dao.update_order', return_value=ORDER)
    get_user_promotion_usage_mock = mocker.patch(
        'DiscountsManagementApp.index.get_user_promotion_usage', return_value=None)
    get_user_by_id_mock = mocker.patch(
        'DiscountsManagementApp.index.get_user_by_id', return_value=user)
    update_availability_mock = mocker.patch(
        'DiscountsManagementApp.index.update_availability')

    res = test_client.patch('/api/orders/1', data={
        'status': 'CANCELLED'
    })

    assert res.status_code == 204
    get_order_mock.assert_called_once_with(1)
    validate_order_update_mock.assert_called_once_with(
        customer_id=1, old_status='PENDING', new_status='CANCELLED')
    update_order_mock.assert_called_once_with(1, status='CANCELLED')
    get_user_promotion_usage_mock.assert_called_once_with(
        user_id=1, promotion_id=1)
    get_user_by_id_mock.assert_called_once_with(1)
    update_availability_mock.assert_called_once_with(
        user=user, promotion=None, user_promotion_usage=None, increment_usage=False)


def test_update_order_status_api_bad_data(test_client, mocker):
    user = FakeUser(user_id=1, is_authenticated=True)
    mocker.patch('flask_login.utils._get_user', return_value=user)

    get_order_mock = mocker.patch(
        'DiscountsManagementApp.index.get_order_by_id', return_value=ORDER)
    validate_order_update_mock = mocker.patch(
        'DiscountsManagementApp.index.validate_order_update', return_value=(False, 'error message test'))

    res = test_client.patch('/api/orders/1', data={
        'status': 'COMPLETED'
    })

    assert res.status_code == 400
    data = res.get_json()
    assert 'error' in data
    assert data == {'error': 'error message test'}
    get_order_mock.assert_called_once_with(1)
    validate_order_update_mock.assert_called_once_with(
        customer_id=1, old_status='PENDING', new_status='COMPLETED')


def test_update_order_status_api_order_not_found(test_client, mocker):
    user = FakeUser(user_id=1, is_authenticated=True)
    mocker.patch('flask_login.utils._get_user', return_value=user)

    get_order_mock = mocker.patch(
        'DiscountsManagementApp.index.get_order_by_id', return_value=None)

    res = test_client.patch('/api/orders/1', data={
        'status': 'COMPLETED'
    })

    assert res.status_code == 404
    data = res.get_json()
    assert 'error' in data
    assert data == {'error': 'Đơn hàng không tồn tại!'}
    get_order_mock.assert_called_once_with(1)


def test_update_order_status_api_exception(test_client, mocker):
    user = FakeUser(user_id=1, is_authenticated=True)
    mocker.patch('flask_login.utils._get_user', return_value=user)

    get_order_mock = mocker.patch(
        'DiscountsManagementApp.index.get_order_by_id', return_value=ORDER)
    validate_order_update_mock = mocker.patch(
        'DiscountsManagementApp.index.validate_order_update', return_value=(True, ''))
    update_order_mock = mocker.patch(
        'DiscountsManagementApp.index.dao.update_order', side_effect=Exception('Database error'))

    res = test_client.patch('/api/orders/1', data={
        'status': 'COMPLETED'
    })

    assert res.status_code == 400
    data = res.get_json()
    assert 'error' in data
    assert data == {
        'error': 'Không thể cập nhật đơn hàng do Database error'}
    get_order_mock.assert_called_once_with(1)
    validate_order_update_mock.assert_called_once_with(
        customer_id=1, old_status='PENDING', new_status='COMPLETED')
    update_order_mock.assert_called_once_with(1, status='COMPLETED')


def test_update_order_status_api_unauthenticated(test_client, mocker):
    mocker.patch('flask_login.utils._get_user',
                 return_value=FakeUser(is_authenticated=False))

    res = test_client.patch('/api/orders/1', data={
        'status': 'COMPLETED'
    })

    assert res.status_code == 401
    assert b'Unauthorized' in res.data


def test_get_promotions_api_success(test_client, mocker):
    PROMOTION.remaining_availability_count = 10

    promotion_result = FakePaginationResult(
        page=1,
        pages=1,
        has_next=False,
        has_prev=False,
        items=[PROMOTION]
    )

    get_promotions_mock = mocker.patch(
        'DiscountsManagementApp.index.dao.get_promotions', return_value=promotion_result)

    res = test_client.get('/api/promotions')

    assert res.status_code == 200
    data = res.get_json()
    assert data['page'] == 1
    assert data['total_pages'] == 1
    assert data['has_next'] is False
    assert data['has_prev'] is False
    assert data['items'] == [PROMOTION.to_dict()]
    get_promotions_mock.assert_called_once_with(
        code=None, page=None, order_value=None, ptype=None
    )


def test_get_promotions_api_invalid_page(test_client):
    res = test_client.get('/api/promotions', query_string={
        'page': '0'
    })

    assert res.status_code == 400
    data = res.get_json()
    assert 'error' in data
    assert data == {'error': 'Số trang không hợp lệ!'}


def test_get_promotions_api_invalid_amount(test_client):
    res = test_client.get('/api/promotions', query_string={
        'amount': 'sdsdsd'
    })

    assert res.status_code == 400
    data = res.get_json()
    assert 'error' in data
    assert data == {'error': 'Giá trị đơn hàng không hợp lệ!'}


def test_create_promotion_api_unauthenticated(test_client, mocker):
    mocker.patch('flask_login.utils._get_user',
                 return_value=FakeUser(is_authenticated=False))

    res = test_client.post('/api/promotions', data={
        'code': 'TEST',
        'promotion_type': 'COUPON',
        'value': 0.10,
        'availability_count': 150,
        'start_date': '2026-03-01 00:00:00',
        'expire_date': '2026-12-31 23:59:59',
        'max_discount_amount': 100000,
        'min_order_value': 0,
        'description': 'test'
    })

    assert res.status_code == 401
    assert b'Unauthorized' in res.data


def test_create_promotion_api_forbidden(test_client, mocker):
    mocker.patch('flask_login.utils._get_user', return_value=FakeUser(
        is_authenticated=True, user_id=1, role=UserRole.CUSTOMER))

    res = test_client.post('/api/promotions', data={
        'code': 'TEST',
        'promotion_type': 'COUPON',
        'value': 0.10,
        'availability_count': 150,
        'start_date': '2026-03-01 00:00:00',
        'expire_date': '2026-12-31 23:59:59',
        'max_discount_amount': 100000,
        'min_order_value': 0,
        'description': 'test'
    })

    assert res.status_code == 403
    data = res.get_json()
    assert 'error' in data
    assert data == {
        'error': 'Bạn không có quyền truy cập tài nguyên này'}


def test_create_promotion_api_validation_error(test_client, mocker):
    mocker.patch('flask_login.utils._get_user', return_value=FakeUser(
        is_authenticated=True, user_id=1, role=UserRole.ADMIN))
    validate_add_promotion_mock = mocker.patch(
        'DiscountsManagementApp.index.validate_add_promotion', return_value=(False, 'error message test'))

    res = test_client.post('/api/promotions', data={
        'code': 'TEST',
        'promotion_type': 'COUPON',
        'value': 0.10,
        'availability_count': 150,
        'start_date': '2026-03-01 00:00:00',
        'expire_date': '2026-12-31 23:59:59',
        'max_discount_amount': 100000,
        'min_order_value': 0,
        'description': 'test'
    })

    assert res.status_code == 400
    data = res.get_json()
    assert 'error' in data
    assert data == {'error': 'error message test'}
    validate_add_promotion_mock.assert_called_once()


def test_create_promotion_api_exception(test_client, mocker):
    mocker.patch('flask_login.utils._get_user', return_value=FakeUser(
        is_authenticated=True, user_id=1, role=UserRole.ADMIN))
    validate_add_promotion_mock = mocker.patch(
        'DiscountsManagementApp.index.validate_add_promotion', return_value=(True, ''))
    add_promotion_mock = mocker.patch(
        'DiscountsManagementApp.index.dao.add_promotion', side_effect=Exception('Database error'))

    res = test_client.post('/api/promotions', data={
        'code': 'TEST',
        'promotion_type': 'COUPON',
        'value': 0.10,
        'availability_count': 150,
        'start_date': '2026-03-01 00:00:00',
        'expire_date': '2026-12-31 23:59:59',
        'max_discount_amount': 100000,
        'min_order_value': 0,
        'description': 'test'
    })

    start_date = datetime.strptime('2026-03-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    expire_date = datetime.strptime('2026-12-31 23:59:59', '%Y-%m-%d %H:%M:%S')

    assert res.status_code == 400
    data = res.get_json()
    assert 'error' in data
    assert data == {
        'error': 'Không thể tạo mã khuyến mãi do Database error'}
    validate_add_promotion_mock.assert_called_once_with(
        'TEST', 'COUPON', 0.10, 150, start_date, expire_date, 100000, 0)
    add_promotion_mock.assert_called_once_with(
        'TEST', 'COUPON', 0.10, 150, start_date, expire_date, 100000, 0, 'test')


def test_create_promotion_api_success(test_client, mocker):
    mocker.patch('flask_login.utils._get_user', return_value=FakeUser(
        is_authenticated=True, user_id=1, role=UserRole.ADMIN))
    validate_add_promotion_mock = mocker.patch(
        'DiscountsManagementApp.index.validate_add_promotion', return_value=(True, ''))
    PROMOTION.remaining_availability_count = 10
    add_promotion_mock = mocker.patch(
        'DiscountsManagementApp.index.dao.add_promotion', return_value=PROMOTION)

    res = test_client.post('/api/promotions', data={
        'code': 'TEST',
        'promotion_type': 'COUPON',
        'value': 0.10,
        'availability_count': 150,
        'start_date': '2026-03-01 00:00:00',
        'expire_date': '2026-12-31 23:59:59',
        'max_discount_amount': 100000,
        'min_order_value': 0,
        'description': 'test'
    })

    start_date = datetime.strptime('2026-03-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    expire_date = datetime.strptime('2026-12-31 23:59:59', '%Y-%m-%d %H:%M:%S')

    assert res.status_code == 201
    data = res.get_json()
    assert data == PROMOTION.to_dict()  
    validate_add_promotion_mock.assert_called_once_with(
        'TEST', 'COUPON', 0.10, 150, start_date, expire_date, 100000, 0)
    add_promotion_mock.assert_called_once_with(
        'TEST', 'COUPON', 0.10, 150, start_date, expire_date, 100000, 0, 'test')