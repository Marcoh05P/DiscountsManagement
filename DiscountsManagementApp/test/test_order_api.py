from DiscountsManagementApp.dao import get_order_by_id, get_promotion_by_code, get_user_promotion_usage
from DiscountsManagementApp.test.test_base import FakeUser, test_app, test_client, test_session, sample_promotion, sample_user_promotion_usage, sample_user, sample_order, time_freezer
import pytest
from DiscountsManagementApp.models import UserRole, Promotion


@pytest.mark.parametrize("user_id, input_amount, input_code, expected_status_code, expected_id, expected_customer_id, expected_promotion_id, expected_sub_total_amount, expected_discount_amount, expected_final_amount, expected_usage_count, error_message", [
    # Mặc định database đã có sẵn 15 orders, nên id của order mới sẽ là 16

    # Thành công với mã loại COUPON
    (1, 800000, 'VIP25', 201, 16, 1, 4, 800000,
     800000*0.25, 800000 - (800000*0.25), 1, None),

    # Thành công với mã loại VOUCHER
    (2, 500000, 'SHIP50K', 201, 16, 2, 11, 500000, 50000, 500000 - 50000, 1, None),

    # Thành công với không sử dụng mã khuyến mãi
    (2, 500000, None, 201, 16, 2, None, 500000, 0, 500000, 0, None),

    # Lỗi với giá trị đơn hàng không hợp lệ
    (1, None, 'VIP25', 400, None, None, None, None,
     None, None, None, 'Giá trị đơn hàng không hợp lệ!'),
    (1, "jkhsadjkask", 'VIP25', 400, None, None, None, None,
     None, None, None, 'Giá trị đơn hàng không hợp lệ!'),
    (1, 0, 'VIP25', 400, None, None, None, None, None,
     None, None, 'Giá trị đơn hàng không hợp lệ!'),

    # Lỗi với mã khuyến mãi không tồn tại
    (1, 800000, 'YITGYTGYIUTYUI', 400, None, None, None,
     None, None, None, None, 'Mã khuyến mãi không tồn tại!'),

    # Lỗi với mã khuyến mãi chưa bắt đầu
    (1, 800000, 'APPONLY8', 400, None, None, None, None,
     None, None, None, 'Mã khuyến mãi chưa bắt đầu!'),

    # Lỗi với mã khuyến mãi đã hết hạn
    (1, 800000, 'SUMMER18', 400, None, None, None, None,
     None, None, None, 'Mã khuyến mãi đã hết hạn!'),

    # Lỗi với mã khuyến mãi đã hết lượt sử dụng
    (1, 800000, 'SAVE15', 400, None, None, None, None, None,
     None, None, 'Mã khuyến mãi đã hết lượt sử dụng!'),

    # Lỗi với giá trị đơn hàng không đủ để áp dụng mã khuyến mãi
    (1, 200000, 'VIP25', 400, None, None, None, None, None, None, None,
     'Giá trị đơn hàng phải lớn hơn hoặc bằng 800000.0 để áp dụng!'),

    # Lỗi với mã khuyến mãi loại COUPON có giá trị giảm giá vượt quá 50% giá trị đơn hàng
    (1, 75000, 'SHIP50K', 400, None, None, None, None, None, None, None,
     'Không thể sử dụng mã khuyến mãi này vì giá trị giảm giá vượt quá 50% giá trị đơn hàng!'),

    # Lỗi với người dùng đã hết lượt sử dụng mã khuyến mãi
    (1, 800000, 'NEW10', 400, None, None, None, None, None, None, None,
        'Bạn đã hết lượt sử dụng mã khuyến mãi này rồi!'),

    # Lỗi với người dùng chưa đăng nhập
    (None, 800000, 'VIP25', 401, None, None, None, None, None, None, None, None),

])
def test_create_order(test_client, mocker, sample_promotion, sample_order, sample_user_promotion_usage, sample_user, user_id, input_amount, input_code, expected_status_code, expected_id, expected_customer_id, expected_promotion_id, expected_sub_total_amount, expected_discount_amount, expected_final_amount, expected_usage_count, error_message):

    fakeUser = FakeUser(is_authenticated=False if user_id is None else True,
                        user_id=user_id)
    mocker.patch("flask_login.utils._get_user", return_value=fakeUser)

    res = test_client.post('/api/orders', data={
        'sub_total_amount': input_amount,
        'promotion_code': input_code
    })
    assert res.status_code == expected_status_code
    data = res.get_json()
    if res.status_code == 201:
        order = get_order_by_id(expected_id)
        assert order is not None
        assert order.id == data['id'] == expected_id
        assert order.customer_id == data['customer_id'] == expected_customer_id
        assert order.promotion_id == data['promotion_id'] == expected_promotion_id
        assert order.sub_total_amount == data['sub_total_amount'] == expected_sub_total_amount
        assert order.discount_amount == data['discount_amount'] == expected_discount_amount
        assert order.final_amount == data['final_amount'] == expected_final_amount

        if expected_promotion_id:
            user_promotion_usage = get_user_promotion_usage(
                user_id=expected_customer_id, promotion_id=expected_promotion_id)
            assert user_promotion_usage is not None
            assert user_promotion_usage.usage_count == expected_usage_count
    elif res.status_code == 400:
        assert data['error'] == error_message


@pytest.mark.parametrize("order_id, input_order_status, user_id, user_role, expected_status_code, expected_order_id, expected_customer_id, expected_order_status, expected_usage_count, expected_remaining_availability_count, error_message", [

    # Thành công cập nhật trạng thái đơn hàng có trạng thái mới giống trạng thái cũ
    (1, 'PENDING', 1, UserRole.CUSTOMER, 204, 1, 1, 'PENDING', 2, 0, None),
    (14, 'COMPLETED', 1, UserRole.CUSTOMER, 204, 14, 1, 'COMPLETED', 2, 148, None),
    (15, 'CANCELLED', 2, UserRole.CUSTOMER, 204, 15, 2, 'CANCELLED', 0, 148, None),

    # Thành công cập nhật trạng thái đơn hàng có trạng thái mới khác trạng thái cũ
    (1, 'COMPLETED', 1, UserRole.CUSTOMER, 204, 1, 1, 'COMPLETED', 2, 0, None),
    (1, 'CANCELLED', 1, UserRole.CUSTOMER, 204, 1, 1, 'CANCELLED', 1, 1, None),
    (1, 'CANCELLED', 4, UserRole.ADMIN, 204, 1, 1, 'CANCELLED', 1, 1, None),


    # Lỗi với đơn hàng không tồn tại
    (999, 'CANCELLED', 1, UserRole.CUSTOMER, 404, None,
     None, None, None, None, 'Đơn hàng không tồn tại!'),

    # Lỗi chưa đăng nhập
    (1, 'CANCELLED', None, None, 401, None, None, None, None, None, None),

    # Lỗi với người dùng không có quyền cập nhật đơn hàng
    (1, 'CANCELLED', 2, UserRole.CUSTOMER, 400, None, None, None,
     None, None, 'Bạn không có quyền cập nhật đơn hàng này.'),

    # Lỗi với trạng thái đơn hàng không hợp lệ
    (1, 'UUIUIUIY', 1, UserRole.CUSTOMER, 400, None, None,
     None, None, None, 'Trạng thái cập nhật không hợp lệ.'),

    # Lỗi cập nhật đơn hàng đã hoàn thành hoặc đã hủy
    (14, 'CANCELLED', 1, UserRole.CUSTOMER, 400, None, None, None, None,
     None, 'Chỉ có thể cập nhật đơn hàng ở trạng thái đang chờ xử lý.'),
    (15, 'COMPLETED', 2, UserRole.CUSTOMER, 400, None, None, None, None,
     None, 'Chỉ có thể cập nhật đơn hàng ở trạng thái đang chờ xử lý.'),


])
def test_update_order_status(test_client, mocker, sample_promotion, sample_order, sample_user_promotion_usage, sample_user, order_id, input_order_status, user_id, user_role, expected_status_code, expected_order_id, expected_customer_id, expected_order_status, expected_usage_count, expected_remaining_availability_count, error_message):

    fakeUser = FakeUser(is_authenticated=False if user_id is None else True,
                        user_id=user_id, role=user_role)
    mocker.patch("flask_login.utils._get_user", return_value=fakeUser)

    res = test_client.patch(f'/api/orders/{order_id}', data={
        'status': input_order_status
    })
    assert res.status_code == expected_status_code
    if res.status_code == 204:
        order = get_order_by_id(order_id)
        assert order is not None
        assert order.id == expected_order_id
        assert order.customer_id == expected_customer_id
        assert order.status.name == expected_order_status

        if order.promotion_id:
            user_promotion_usage = get_user_promotion_usage(
                user_id=order.customer_id, promotion_id=order.promotion_id)
            assert user_promotion_usage is not None
            assert user_promotion_usage.usage_count == expected_usage_count

            promotion = Promotion.query.get(order.promotion_id)
            promotion = get_promotion_by_code(promotion.code)
            assert promotion is not None
            assert promotion.remaining_availability_count == expected_remaining_availability_count

    elif res.status_code == 400 or res.status_code == 404:
        data = res.get_json()
        assert data['error'] == error_message


def test_update_order_status_invalid_order_id(test_client, mocker):
    fakeUser = FakeUser(is_authenticated=True, user_id=1,
                        role=UserRole.CUSTOMER)
    mocker.patch("flask_login.utils._get_user", return_value=fakeUser)

    res = test_client.patch('/api/orders/invalid_id', data={
        'status': 'CANCELLED'
    })
    assert res.status_code == 404
