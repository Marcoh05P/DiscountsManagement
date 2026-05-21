import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from DiscountsManagementApp.test.pages.BasePage import BasePage


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
    SEARCH_INPUT = (By.NAME, 'search')
    SEARCH_BUTTON = (By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
    def open_page(self):
        self.open(self.URL)

    def open_create_page(self):
        self.open(self.CREATE_URL)

    def set_value_by_js(self, by, value, text):
        e = self.find(by, value)
        self.driver.execute_script(
            """
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """,
            e,
            text
        )

    def select_promotion_type(self, promotion_type):
        select_element = self.find(*self.PROMOTION_TYPE)

        try:
            select = Select(select_element)
            select.select_by_visible_text(promotion_type)
        except:
            self.driver.execute_script(
                """
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                """,
                select_element,
                promotion_type
            )

    def create_promotion(
            self,
            code,
            promotion_type='COUPON',
            start_date='22/05/2026 00:00',
            expire_date='31/12/2026 23:59',
            availability_count='100',
            value='0.1',
            max_discount_amount='100000',
            min_order_value='100000',
            description='Selenium test promotion'
    ):
        self.set_value_by_js(*self.CODE, code)
        self.select_promotion_type(promotion_type)

        self.set_value_by_js(*self.START_DATE, start_date)
        self.set_value_by_js(*self.EXPIRE_DATE, expire_date)
        self.set_value_by_js(*self.AVAILABILITY_COUNT, availability_count)
        self.set_value_by_js(*self.VALUE, value)
        self.set_value_by_js(*self.MAX_DISCOUNT_AMOUNT, max_discount_amount)
        self.set_value_by_js(*self.MIN_ORDER_VALUE, min_order_value)
        self.set_value_by_js(*self.DESCRIPTION, description)

        time.sleep(1)
        self.click(*self.SAVE_BUTTON)

    def create_coupon(
            self,
            code,
            value='0.1',
            start_date='22/05/2026 00:00',
            expire_date='31/12/2026 23:59'
    ):
        self.create_promotion(
            code=code,
            promotion_type='COUPON',
            value=value,
            start_date=start_date,
            expire_date=expire_date,
            max_discount_amount='100000',
            description='Coupon test by Selenium'
        )

    def create_voucher(self, code, value='20000', start_date='22/05/2026 00:00'):
        self.create_promotion(
            code=code,
            promotion_type='VOUCHER',
            value=value,
            start_date=start_date,
            max_discount_amount='0',
            description='Voucher test by Selenium'
        )

    def search_promotion(self, code):
        self.open_page()
        self.typing(*self.SEARCH_INPUT, code)
        self.click(*self.SEARCH_BUTTON)
        time.sleep(1)

    def delete_promotion_by_code(self, code):
        self.search_promotion(code)

        delete_button = (
            By.XPATH,
            "//tr[contains(., '" + code + "')]//button[contains(@title, 'Delete') or contains(@class, 'delete') or .//span[contains(@class, 'trash')] or .//i[contains(@class, 'trash')]]"
        )

        button = self.find(*delete_button)
        self.driver.execute_script("arguments[0].click();", button)

        time.sleep(1)

        try:
            alert = self.driver.switch_to.alert
            alert.accept()
        except:
            pass

        time.sleep(1)