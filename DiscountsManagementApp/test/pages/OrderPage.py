import time
from selenium.webdriver.common.by import By
from DiscountsManagementApp.test.pages.BasePage import BasePage


class OrderPage(BasePage):
    URL = 'http://127.0.0.1:5000/order_create'
    HISTORY_URL = 'http://127.0.0.1:5000/orders_history'

    AMOUNT_INPUT = (By.ID, 'amount-input')
    CODE_INPUT = (By.ID, 'code')
    CREATE_ORDER_BUTTON = (By.ID, 'create-order-btn')
    ORDER_INFO = (By.ID, 'order-info')
    PROMOTIONS_LIST = (By.ID, 'promotions-list')
    HISTORY_TABLE = (By.TAG_NAME, 'table')
    EMPTY_HISTORY_ALERT = (By.CLASS_NAME, 'alert-info')

    PROMOTION_ITEM = (By.CLASS_NAME, 'promotion-item')
    ERROR_MESSAGE = (By.ID, 'error-message')

    def open_page(self):
        self.open(self.URL)

    def open_history_page(self):
        self.open(self.HISTORY_URL)

    def input_amount(self, amount):
        self.typing(*self.AMOUNT_INPUT, str(amount))

    def search_promotion(self, code):
        e = self.find(*self.CODE_INPUT)
        e.clear()
        e.send_keys(code)

    def choose_first_promotion(self):
        self.click(*self.PROMOTION_ITEM)

    def choose_promotion_by_code(self, code):
        promotion = (
            By.XPATH,
            "//*[contains(@class, 'promotion-item') and contains(., '" + code + "')]"
        )
        self.click(*promotion)

    def create_order(self):
        button = self.find(*self.CREATE_ORDER_BUTTON)
        self.driver.execute_script("arguments[0].scrollIntoView();", button)
        self.driver.implicitly_wait(1)
        self.driver.execute_script("arguments[0].click();", button)

    def create_order_with_promotion(self, amount, code):
        self.input_amount(amount)
        time.sleep(1)

        self.search_promotion(code)
        time.sleep(2)

        self.choose_promotion_by_code(code)
        time.sleep(1)

        self.create_order()

    def create_order_without_promotion(self, amount):
        self.input_amount(amount)
        self.driver.implicitly_wait(1)

        self.create_order()

    def get_error_message(self):
        return self.find(*self.ERROR_MESSAGE).text