from flask import jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from DiscountsManagementApp import app, dao
from DiscountsManagementApp.dao import check_phone_number_exists, get_promotion_by_code
from DiscountsManagementApp.models import UserRole
from DiscountsManagementApp.utils import update_availability
from DiscountsManagementApp.validators.base import validate_registration_data, validate_order_data


def _default_redirect_for_role(user):
    if user.role == UserRole.ADMIN:
        return '/admin/'
    return url_for('index')


@app.route("/")
def index():
    kw = request.args.get('kw')
    sort = request.args.get('sort')
    page = request.args.get('page', 1, type=int)
    promotions = dao.get_promotions(kw, sort_by=sort, page=page)

    return render_template("index.html", promotions=promotions)


@app.route('/login', methods=['GET', 'POST'])
def login_view():
    err_msg = ''
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')

        user = dao.auth_user(phone_number, password)

        if user:
            login_user(user=user)
            next_page = request.args.get('next')
            return redirect(next_page or _default_redirect_for_role(user))
        else:
            err_msg = 'Số điện thoại hoặc mật khẩu không đúng!'

    return render_template('login.html', err_msg=err_msg)


@app.route('/register', methods=['GET', 'POST'])
def register_view():
    err_msg = ''
    if request.method == 'POST':
        data = request.form
        phone_number = data.get('phone_number')
        full_name = data.get('full_name')
        password = data.get('password')
        confirm = data.get('confirm')

        is_valid, error_message = validate_registration_data(
            full_name, phone_number, password, confirm)

        if not is_valid:
            err_msg = error_message
        elif check_phone_number_exists(phone_number):
            err_msg = 'Số điện thoại đã được sử dụng!'
        else:
            try:
                dao.add_user(
                    phone_number=phone_number,
                    password=password,
                    full_name=full_name
                )
                current_user = dao.auth_user(phone_number, password)
                login_user(user=current_user)
                return redirect(url_for('index'))
            except Exception as ex:
                err_msg = f'Hệ thống có lỗi: {str(ex)}'

    return render_template('register.html', err_msg=err_msg)


@app.route('/logout')
def logout_process():
    logout_user()
    return redirect(url_for('index'))


@app.route('/order_create', methods=['GET'])
@login_required
def order_create_view():
    return render_template('order_create.html')


@app.route('/orders_history')
@login_required
def orders_history():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'newest')
    orders = dao.get_orders_by_customer(
        current_user.id, page=page, sort_by=sort)
    return render_template('orders_history.html', orders=orders, sort=sort)


@app.route('/api/orders', methods=['POST'])
@login_required
def create_order():
    promotion_code = request.form.get('promotion_code')
    sub_total_amount = request.form.get('sub_total_amount', type=float)
    print(
        f'Promotion code: {promotion_code}, Sub total amount: {sub_total_amount}')
    promotion = None
    user_promotion_usage = None
    discount_amount = 0.0
    if promotion_code:
        promotion = get_promotion_by_code(promotion_code)
        if promotion:
            discount_amount = promotion.promotion_type.get_discount_calculator()(
                sub_total_amount, promotion.max_discount_amount, promotion.value)
            user_promotion_usage = dao.get_user_promotion_usage(
                current_user.id, promotion.id)
        is_using_promotion = True
    else:
        is_using_promotion = False

    is_valid, error_message = validate_order_data(current_user, sub_total_amount=sub_total_amount,
                                                  promotion=promotion, promotion_usage=user_promotion_usage,
                                                  is_using_promotion=is_using_promotion, discount_amount=discount_amount)
    if not is_valid:
        err_msg = error_message
    else:
        try:
            order = dao.create_order(
                customer_id=current_user.id,
                sub_total_amount=sub_total_amount,
                discount_amount=discount_amount,
                final_amount=float(sub_total_amount) - discount_amount,
                promotion_id=promotion.id if promotion else None
            )
            if promotion:
                update_availability(
                    current_user, promotion, user_promotion_usage=user_promotion_usage, increment_usage=True)

            return jsonify(order.to_dict()), 201
        except Exception as ex:
            err_msg = f'Không thể tạo đơn hàng do {str(ex)}'
    return jsonify({'error': err_msg}), 400


@app.route('/api/promotions', methods=['GET'])
def get_promotions():
    code = request.args.get('code')
    amount = request.args.get('amount', type=float)
    ptype = request.args.get('ptype')
    page = request.args.get('page', 1, type=int)
    promotions = dao.get_promotions(code=code, page=page, order_value=amount, ptype=ptype)
    return jsonify({
        'page': promotions.page,
        'total_pages': promotions.pages,
        'has_next': promotions.has_next,
        'has_prev': promotions.has_prev,
        'items': [item.to_dict() for item in promotions.items]
    })

