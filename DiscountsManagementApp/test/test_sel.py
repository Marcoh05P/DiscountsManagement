import time

from DiscountsManagementApp.test.pages.HomePage import HomePage
from DiscountsManagementApp.test.pages.LoginPage import LoginPage
from DiscountsManagementApp.test.test_base import driver, selenium_data

from DiscountsManagementApp.test.pages.RegisterPage import RegisterPage
from DiscountsManagementApp.test.pages.OrderPage import OrderPage
from DiscountsManagementApp.test.pages.PromotionAdminPage import PromotionAdminPage
ADMIN_PHONE = "0706823664"
ADMIN_PASSWORD = "123456"

SEL_USER_PHONE = "0911111111"
SEL_USER_PASSWORD = "Sel123@@"
SEL_PROMOTION_CODE = "SEL10"
SEL_EXPIRED_PROMOTION_CODE = "SELEXPIRED"
SEL_OUT_OF_USAGE_PROMOTION_CODE = "SELOUT"
SEL_VOUCHER_CODE = "SELVOUCHER"
SEL_NOT_STARTED_PROMOTION_CODE = "SELSTART"

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

def test_guest_cannot_access_create_order(driver):
    driver.get('http://127.0.0.1:5000/order_create')

    time.sleep(1)

    assert 'Unauthorized' in driver.page_source

def test_user_can_access_create_order_after_login(driver, selenium_data):
    login = LoginPage(driver)
    login.open_page()
    login.login(SEL_USER_PHONE, SEL_USER_PASSWORD)

    time.sleep(1)

    order = OrderPage(driver)
    order.open_page()

    time.sleep(1)

    assert 'Unauthorized' not in driver.page_source
    assert 'order_create' in driver.current_url

def test_selenium_customer_login_success(driver, selenium_data):
    login = LoginPage(driver)
    login.open_page()
    login.login(SEL_USER_PHONE, SEL_USER_PASSWORD)

    time.sleep(1)

    assert 'Số điện thoại hoặc mật khẩu không đúng' not in driver.page_source
    assert driver.current_url != 'http://127.0.0.1:5000/login'

def test_create_order_without_promotion(driver, selenium_data):
    login = LoginPage(driver)
    login.open_page()
    login.login(SEL_USER_PHONE, SEL_USER_PASSWORD)

    time.sleep(3)

    order = OrderPage(driver)
    order.open_page()

    time.sleep(3)

    order.create_order_without_promotion(500000)

    time.sleep(3)

    assert 'orders_history' in driver.current_url

def test_create_order_with_valid_promotion(driver, selenium_data):
    login = LoginPage(driver)
    login.open_page()
    login.login(SEL_USER_PHONE, SEL_USER_PASSWORD)

    time.sleep(3)

    order = OrderPage(driver)
    order.open_page()

    time.sleep(3)

    order.create_order_with_promotion(500000, SEL_PROMOTION_CODE)

    time.sleep(3)

    assert 'orders_history' in driver.current_url
    assert '450,000 VNĐ' in driver.page_source

def test_expired_promotion_not_displayed(driver, selenium_data):
    login = LoginPage(driver)
    login.open_page()
    login.login(SEL_USER_PHONE, SEL_USER_PASSWORD)

    time.sleep(3)

    order = OrderPage(driver)
    order.open_page()

    time.sleep(3)

    order.input_amount(500000)
    time.sleep(1)

    order.search_promotion(SEL_EXPIRED_PROMOTION_CODE)
    time.sleep(1)

    assert SEL_EXPIRED_PROMOTION_CODE not in driver.page_source

def test_create_order_below_min_value_promotion_fail(driver, selenium_data):
    login = LoginPage(driver)
    login.open_page()
    login.login(SEL_USER_PHONE, SEL_USER_PASSWORD)

    time.sleep(3)

    order = OrderPage(driver)
    order.open_page()

    time.sleep(3)

    order.input_amount(50000)

    time.sleep(1)

    order.search_promotion(SEL_PROMOTION_CODE)

    time.sleep(1)

    assert SEL_PROMOTION_CODE not in driver.page_source

def test_out_of_usage_promotion_not_displayed(driver, selenium_data):
    login = LoginPage(driver)
    login.open_page()
    login.login(SEL_USER_PHONE, SEL_USER_PASSWORD)

    time.sleep(3)

    order = OrderPage(driver)
    order.open_page()

    time.sleep(3)

    order.input_amount(500000)

    time.sleep(3)

    order.search_promotion(SEL_OUT_OF_USAGE_PROMOTION_CODE)

    time.sleep(3)

    assert SEL_OUT_OF_USAGE_PROMOTION_CODE not in driver.page_source

def test_create_order_with_valid_voucher(driver, selenium_data):
    login = LoginPage(driver)
    login.open_page()
    login.login(SEL_USER_PHONE, SEL_USER_PASSWORD)

    time.sleep(3)

    order = OrderPage(driver)
    order.open_page()

    time.sleep(3)

    order.create_order_with_promotion(500000, SEL_VOUCHER_CODE)

    time.sleep(3)

    assert 'orders_history' in driver.current_url
    assert '480,000 VNĐ' in driver.page_source

def test_create_order_amount_equal_min_value_success(driver, selenium_data):
    login = LoginPage(driver)
    login.open_page()
    login.login(SEL_USER_PHONE, SEL_USER_PASSWORD)

    time.sleep(3)

    order = OrderPage(driver)
    order.open_page()

    time.sleep(3)

    order.create_order_with_promotion(100000, SEL_PROMOTION_CODE)

    time.sleep(3)

    assert 'orders_history' in driver.current_url
    assert '90,000 VNĐ' in driver.page_source

def test_not_started_promotion_not_displayed(driver, selenium_data):
    login = LoginPage(driver)
    login.open_page()
    login.login(SEL_USER_PHONE, SEL_USER_PASSWORD)

    time.sleep(3)

    order = OrderPage(driver)
    order.open_page()

    time.sleep(3)

    order.input_amount(500000)

    time.sleep(1)

    order.search_promotion(SEL_NOT_STARTED_PROMOTION_CODE)

    time.sleep(1)

    assert SEL_NOT_STARTED_PROMOTION_CODE not in driver.page_source


def test_customer_cannot_access_admin_promotion_page(driver, selenium_data):
    login = LoginPage(driver)
    login.open_page()
    login.login(SEL_USER_PHONE, SEL_USER_PASSWORD)

    time.sleep(3)

    driver.get('http://127.0.0.1:5000/admin/promotion/')

    time.sleep(1)

    assert 'admin/promotion' not in driver.current_url or 'Forbidden' in driver.page_source or 'login' in driver.current_url

def test_admin_can_access_admin_promotion_page(driver):
    login = LoginPage(driver)
    login.open_page()
    login.login(ADMIN_PHONE, ADMIN_PASSWORD)

    time.sleep(3)

    driver.get('http://127.0.0.1:5000/admin/promotion/')

    time.sleep(1)

    assert 'admin/promotion' in driver.current_url
    assert 'Forbidden' not in driver.page_source
    assert 'Unauthorized' not in driver.page_source

def test_admin_create_coupon_success(driver):
    login = LoginPage(driver)
    login.open_page()
    login.login(ADMIN_PHONE, ADMIN_PASSWORD)

    time.sleep(3)

    promotion_admin = PromotionAdminPage(driver)
    promotion_admin.open_create_page()

    time.sleep(2)

    code = 'S' + str(int(time.time()))[-8:]

    promotion_admin.create_coupon(code)

    time.sleep(3)

    assert 'admin/promotion' in driver.current_url
    assert 'Record was successfully created' in driver.page_source

def test_admin_create_duplicate_coupon_fail(driver):
    login = LoginPage(driver)
    login.open_page()
    login.login(ADMIN_PHONE, ADMIN_PASSWORD)

    time.sleep(3)

    promotion_admin = PromotionAdminPage(driver)

    code = 'D' + str(int(time.time()))[-8:]

    promotion_admin.open_create_page()
    time.sleep(2)
    promotion_admin.create_coupon(code)

    time.sleep(3)

    assert 'admin/promotion' in driver.current_url
    assert 'Record was successfully created' in driver.page_source

    promotion_admin.open_create_page()
    time.sleep(2)
    promotion_admin.create_coupon(code)

    time.sleep(3)

    assert (
        'admin/promotion/new' in driver.current_url
        or 'đã tồn tại' in driver.page_source.lower()
        or 'already exists' in driver.page_source.lower()
        or 'unique' in driver.page_source.lower()
    )

def test_admin_create_coupon_over_50_percent_fail(driver):
    login = LoginPage(driver)
    login.open_page()
    login.login(ADMIN_PHONE, ADMIN_PASSWORD)

    time.sleep(3)

    promotion_admin = PromotionAdminPage(driver)
    promotion_admin.open_create_page()

    time.sleep(2)

    code = 'P' + str(int(time.time()))[-6:]

    promotion_admin.create_coupon(code, value='0.6')

    time.sleep(3)

    assert 'admin/promotion/new' in driver.current_url
    assert (
        '50' in driver.page_source
        or 'không vượt quá' in driver.page_source.lower()
        or 'không hợp lệ' in driver.page_source.lower()
        or 'giá trị' in driver.page_source.lower()
    )

def test_order_created_status_is_pending(driver, selenium_data):
    login = LoginPage(driver)
    login.open_page()
    login.login(SEL_USER_PHONE, SEL_USER_PASSWORD)

    time.sleep(3)

    order = OrderPage(driver)
    order.open_page()

    time.sleep(3)

    order.create_order_without_promotion(500000)

    time.sleep(3)

    assert 'orders_history' in driver.current_url
    assert 'Chờ xử lý' in driver.page_source
    assert 'Hoàn thành' in driver.page_source
    assert 'Hủy' in driver.page_source