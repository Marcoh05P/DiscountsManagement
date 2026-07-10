# 💳Discount Management

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-black?logo=flask)
![pytest](https://img.shields.io/badge/pytest-Test%20Suite-0A9EDC?logo=pytest&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-UI%20Testing-43B02A?logo=selenium&logoColor=white)

Discount Management is a Flask project for managing discount codes, orders, and users.

The main goal of this project is testing business rules. It has unit tests, API tests, and Selenium UI tests. These tests check login, register, promotion rules, order creation, order updates, and admin flows.

## Main Features

- User register, login, and logout
- Promotion list, search, and validation
- Order create with and without promotion
- Order history for customer
- Admin management for users, promotions, and orders
- Soft delete for data that should stay in the system

## Testing Focus

This project is designed to verify business logic in many layers:

- Unit tests check validators and DAO functions
- API tests check request and response behavior
- Selenium tests check real browser flows

Some important test cases in this project are:

- Register with valid and invalid data
- Login with correct and wrong password
- Search promotions by code
- Create order without promotion
- Create order with coupon or voucher
- Reject expired, not started, or out-of-usage promotions
- Update order status with correct permission rules
- Block guest users from private pages

## Tech Stack

- Python
- Flask
- Flask-Admin
- Flask-Login
- Flask-SQLAlchemy
- MySQL for normal run
- SQLite in memory for tests
- pytest
- Selenium

## Project Structure

- DiscountsManagementApp/ main application code
- DiscountsManagementApp/test/ test cases and Selenium page objects
- DiscountsManagementApp/templates/ HTML templates
- DiscountsManagementApp/static/ CSS and JavaScript files
- Database/createPromotions.sql sample promotion data
- run.py application entry point

## Requirements

- Python 3.11+ is recommended
- MySQL server running locally
- A database named discounts_db

The default database setting is:

```text
mysql+pymysql://root:root@localhost/discounts_db?charset=utf8mb4
```

## Setup

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create the database and load sample promotions:

```sql
CREATE DATABASE discounts_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Then run the SQL file in Database/createPromotions.sql.

## Run the App

```bash
python run.py
```

Open the app at:

```text
http://127.0.0.1:5000/
```

## Run Tests

Run all tests with pytest:

```bash
pytest
```

Run one test file if needed:

```bash
pytest DiscountsManagementApp/test/test_validators.py
pytest DiscountsManagementApp/test/test_register_user.py
pytest DiscountsManagementApp/test/test_controller.py
```

## Test Data

The test suite uses sample users, promotions, orders, and promotion usage data.

- test_base.py creates an in-memory database for unit and API tests
- Selenium tests use prepared accounts and promotions
- Sample promotions cover active, expired, not started, and out-of-usage cases

## Notes

- Admin pages are protected by role checks
- Promotion rules depend on promotion type: COUPON and VOUCHER
- Order status logic is covered by tests, especially cancel and complete flows
- If you change business rules, update the related tests first or at the same time

*© 2026 - UniDocs - Developed and tested by Ngàn Thành Phú, Hoàng Phi Hùng, Dương Lê Kim Phụng - Ho Chi Minh City Open University*