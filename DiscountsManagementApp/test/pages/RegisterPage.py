from selenium.webdriver.common.by import By
from DiscountsManagementApp.test.pages.BasePage import BasePage


class RegisterPage(BasePage):
    URL = 'http://127.0.0.1:5000/register'

    PHONE = (By.ID, 'phone_number')
    FULL_NAME = (By.ID, 'full_name')
    PASSWORD = (By.ID, 'password')
    CONFIRM = (By.ID, 'confirm')
    REGISTER_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")

    def open_page(self):
        self.open(self.URL)

    def register(self, phone, full_name, password, confirm):
        self.typing(*self.PHONE, phone)
        self.typing(*self.FULL_NAME, full_name)
        self.typing(*self.PASSWORD, password)
        self.typing(*self.CONFIRM, confirm)
        self.click(*self.REGISTER_BUTTON)