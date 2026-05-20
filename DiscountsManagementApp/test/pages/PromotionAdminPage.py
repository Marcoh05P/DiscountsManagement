import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from DiscountsManagementApp.test.pages.BasePage import BasePage
from selenium.webdriver.common.keys import Keys

class PromotionAdminPage(BasePage):
    URL = 'http://127.0.0.1:5000/admin/promotion/'
    CREATE_URL = 'http://127.0.0.1:5000/admin/promotion/new/'

    CODE = (By.NAME, 'code')
    PROMOTION_TYPE = (By.NAME, 'promotion_type')
    START_DATE = (By.NAME, 'start_date')
    EXPIRE_DATE = (By.NAME, 'expire_date')
    AVAILABILITY_COUNT = (By.NAME, 'availability_count')
    VALUE = (By.NAME, 'value')
    MAX_DISCOUNT_AMOUNT = (By.NAME, 'max_discount_amount')
    MIN_ORDER_VALUE = (By.NAME, 'min_order_value')
    DESCRIPTION = (By.NAME, 'description')
    SAVE_BUTTON = (By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")

    def open_page(self):
        self.open(self.URL)

    def open_create_page(self):
        self.open(self.CREATE_URL)

    def create_coupon(self, code, value='0.1'):
        self.typing(*self.CODE, code)

        select = Select(self.find(*self.PROMOTION_TYPE))
        select.select_by_visible_text('COUPON')

        self.typing_date(*self.START_DATE, '20/05/2026 00:00')
        self.typing_date(*self.EXPIRE_DATE, '31/12/2026 23:59')
        self.typing(*self.AVAILABILITY_COUNT, '100')
        self.typing(*self.VALUE, value)
        self.typing(*self.MAX_DISCOUNT_AMOUNT, '100000')
        self.typing(*self.MIN_ORDER_VALUE, '100000')

        time.sleep(1)

        self.click(*self.SAVE_BUTTON)

    def typing_date(self, by, value, text):
        e = self.find(by, value)
        self.driver.execute_script("arguments[0].value = '';", e)
        self.driver.execute_script("arguments[0].value = arguments[1];", e, text)