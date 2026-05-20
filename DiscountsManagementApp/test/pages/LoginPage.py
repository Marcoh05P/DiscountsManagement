from selenium.webdriver.common.by import By
from DiscountsManagementApp.test.pages.BasePage import BasePage


class LoginPage(BasePage):
    URL = 'http://127.0.0.1:5000/login'
    PHONE = (By.NAME, 'phone_number')
    PASSWORD = (By.NAME, 'password')
    BTN = (By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")

    def open_page(self, url=URL):
        self.open(url)

    def login(self, phone, password):
        self.typing(*self.PHONE, phone)
        self.typing(*self.PASSWORD, password)
        self.click(*self.BTN)