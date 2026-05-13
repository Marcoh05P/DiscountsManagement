import time

from DiscountsManagementApp.test.pages.HomePage import HomePage
from DiscountsManagementApp.test.pages.LoginPage import LoginPage
from DiscountsManagementApp.test.test_base import driver

from selenium.webdriver.common.by import By
from DiscountsManagementApp.test.pages.RegisterPage import RegisterPage
from DiscountsManagementApp.test.pages.OrderPage import OrderPage

ADMIN_PHONE = "0706823664"
ADMIN_PASSWORD = "123456"


def test_login_success(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login(ADMIN_PHONE, ADMIN_PASSWORD)

    time.sleep(1)
    assert driver.current_url != 'http://127.0.0.1:5000/login'


def test_login_wrong_password(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login(ADMIN_PHONE, "wrongpassword")

    time.sleep(1)
    assert driver.current_url == 'http://127.0.0.1:5000/login'


def test_home_search_promotion(driver):
    kw = 'SUPER40'

    home = HomePage(driver=driver)
    home.open_page()
    home.search(kw)

    time.sleep(1)

    assert kw in driver.page_source


def test_logout_success(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login(ADMIN_PHONE, ADMIN_PASSWORD)

    time.sleep(1)

    driver.get('http://127.0.0.1:5000/logout')

    time.sleep(1)
    assert driver.current_url == 'http://127.0.0.1:5000/'

def test_guest_cannot_access_admin_order(driver):
    driver.get('http://127.0.0.1:5000/admin/order/')

    time.sleep(1)

    assert 'login' in driver.current_url


def test_register_password_confirm_not_match(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register(
        phone='0987654321',
        full_name='Dương Lê Kim Phụng',
        password='Phu123@@',
        confirm='Phu123@@@'
    )

    time.sleep(1)

    assert driver.current_url == 'http://127.0.0.1:5000/register'
    assert 'mật khẩu' in driver.page_source.lower()

def test_register_success(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    phone = '09' + str(int(time.time()))[-8:]

    register.register(
        phone=phone,
        full_name='Dương Lê Kim Phụng',
        password='Phu123@@',
        confirm='Phu123@@'
    )

    time.sleep(1)

    assert driver.current_url == 'http://127.0.0.1:5000/'
    assert 'Dương Lê Kim Phụng' in driver.page_source

