import time

from DiscountsManagementApp.test.pages.HomePage import HomePage
from DiscountsManagementApp.test.pages.LoginPage import LoginPage
from DiscountsManagementApp.test.test_base import driver


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

