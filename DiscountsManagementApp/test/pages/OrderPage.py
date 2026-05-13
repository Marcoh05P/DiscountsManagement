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

    def open_page(self):
        self.open(self.URL)

    def open_history_page(self):
        self.open(self.HISTORY_URL)

    def input_amount(self, amount):
        self.typing(*self.AMOUNT_INPUT, str(amount))

    def search_promotion(self, code):
        self.typing(*self.CODE_INPUT, code)

    def create_order(self):
        self.click(*self.CREATE_ORDER_BUTTON)