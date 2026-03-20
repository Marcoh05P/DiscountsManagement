from flask import redirect, render_template, request, url_for
from flask_login import login_user

from DiscountsManagementApp import app, dao


@app.route("/")
def index():
    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login_view():
    err_msg = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username, password)

        if user:
            login_user(user=user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            err_msg = 'Tên đăng nhập hoặc mật khẩu không đúng!'

    return render_template('login.html', err_msg=err_msg)