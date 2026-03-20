from functools import wraps

from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from DiscountsManagementApp import app, dao
from DiscountsManagementApp.dao import check_phone_number_exists
from DiscountsManagementApp.models import UserRole
from DiscountsManagementApp.utils import validate_registration_data

def role_required(*roles):
    def decorator(func):
        @wraps(func)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.role not in roles:
                return redirect(url_for('index'))
            return func(*args, **kwargs)
        return wrapper
    return decorator

def _default_redirect_for_role(user):
    if user.role == UserRole.ADMIN:
        return '/admin/'
    return url_for('index')

@app.route("/")
def index():
    return render_template("index.html")

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
        
        is_valid, error_message = validate_registration_data(full_name, phone_number, password, confirm)
        
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

@app.route('/order_create')
def order_create():
    return render_template('order_create.html')

@app.route('/orders_history')
def orders_history():
    return render_template('orders_history.html')