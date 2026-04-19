from ctypes.util import test
from datetime import datetime
import hashlib

import pytest
from flask import Flask

from DiscountsManagementApp import db
from DiscountsManagementApp.dao import create_order
from DiscountsManagementApp.index import register_routes
from DiscountsManagementApp.models import Promotion, PromotionType, User, UserPromotionUsage


def create_test_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["PAGE_SIZE"] = 3
    app.config["TESTING"] = True
    db.init_app(app)
    register_routes(app)

    return app


@pytest.fixture
def test_client(test_app):
    return test_app.test_client()


@pytest.fixture
def test_app():
    app = create_test_app()
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_session(test_app):
    yield db.session
    db.session.rollback()


'''
Dữ liệu mẫu bao gồm 20 mã khuyến mãi:
- 4 mã COUPON đã có hiệu lực, chưa hết hạn, còn số lượt sử dụng
- 2 mã COUPON chưa hết hạn, nhưng đã hết lượt sử dụng
- 2 mã COUPON đã hết hạn, trong đó 1 mã đã hết lượt sử dụng
- 2 mã COUPON thời gian hiệu lực chưa bắt đầu
- 4 mã VOUCHER đã có hiệu lực, chưa hết hạn, còn số lượt sử dụng
- 2 mã VOUCHER chưa hết hạn, nhưng đã hết lượt sử dụng
- 2 mã VOUCHER đã hết hạn, trong đó 1 mã đã hết lượt sử dụng
- 2 mã VOUCHER thời gian hiệu lực chưa bắt đầu
=====================================================================
Tổng cộng:
- 8 mã còn hiệu lực, chưa hết hạn, còn số lượt sử dụng
- 4 mã chưa hết hạn, nhưng đã hết lượt sử dụng
- 2 mã đã hết hạn, còn số lượt sử dụng
- 2 mã đã hết hạn, đã hết lượt sử dụng
- 4 mã thời gian hiệu lực chưa bắt đầu
'''
@pytest.fixture
def sample_promotion(test_session):
    promotions = [
        Promotion(
            code='NEW10',
            start_date=datetime(2026, 3, 1, 0, 0, 0),
            expire_date=datetime(2026, 12, 31, 23, 59, 59),
            promotion_type=PromotionType.COUPON,
            availability_count=150,
            value=0.10,
            max_discount_amount=100000,
            min_order_value=0,
            description='Giam 10% cho khach hang moi'
        ),
        Promotion(
            code='SAVE15',
            start_date=datetime(2026, 3, 10, 0, 0, 0),
            expire_date=datetime(2026, 11, 30, 23, 59, 59),
            promotion_type=PromotionType.COUPON,
            availability_count=2,
            value=0.15,
            max_discount_amount=180000,
            min_order_value=300000,
            description='Giam 15% don tu 300k'
        ),
        Promotion(
            code='FLASH20',
            start_date=datetime(2026, 4, 1, 0, 0, 0),
            expire_date=datetime(2026, 6, 30, 23, 59, 59),
            promotion_type=PromotionType.COUPON,
            availability_count=2,
            value=0.20,
            max_discount_amount=200000,
            min_order_value=500000,
            description='Flash sale giam 20%'
        ),
        Promotion(
            code='VIP25',
            start_date=datetime(2026, 1, 1, 0, 0, 0),
            expire_date=datetime(2026, 12, 31, 23, 59, 59),
            promotion_type=PromotionType.COUPON,
            availability_count=5,
            value=0.25,
            max_discount_amount=300000,
            min_order_value=800000,
            description='Uu dai VIP giam 25%'
        ),
        Promotion(
            code='WEEKEND5',
            start_date=datetime(2026, 3, 1, 0, 0, 0),
            expire_date=datetime(2026, 8, 31, 23, 59, 59),
            promotion_type=PromotionType.COUPON,
            availability_count=200,
            value=0.05,
            max_discount_amount=50000,
            min_order_value=100000,
            description='Cuoi tuan giam 5%'
        ),
        Promotion(
            code='MORNING12',
            start_date=datetime(2026, 3, 15, 0, 0, 0),
            expire_date=datetime(2026, 9, 30, 23, 59, 59),
            promotion_type=PromotionType.COUPON,
            availability_count=140,
            value=0.12,
            max_discount_amount=120000,
            min_order_value=250000,
            description='Khung gio sang giam 12%'
        ),
        Promotion(
            code='APPONLY8',
            start_date=datetime(2026, 7, 1, 0, 0, 0),
            expire_date=datetime(2026, 10, 31, 23, 59, 59),
            promotion_type=PromotionType.COUPON,
            availability_count=160,
            value=0.08,
            max_discount_amount=80000,
            min_order_value=120000,
            description='Danh rieng cho don app'
        ),
        Promotion(
            code='SUMMER18',
            start_date=datetime(2026, 1, 1, 0, 0, 0),
            expire_date=datetime(2026, 1, 31, 23, 59, 59),
            promotion_type=PromotionType.COUPON,
            availability_count=90,
            value=0.18,
            max_discount_amount=220000,
            min_order_value=450000,
            description='Mua he giam 18%'
        ),
        Promotion(
            code='LOYAL7',
            start_date=datetime(2026, 7, 15, 0, 0, 0),
            expire_date=datetime(2026, 12, 31, 23, 59, 59),
            promotion_type=PromotionType.COUPON,
            availability_count=300,
            value=0.07,
            max_discount_amount=70000,
            min_order_value=100000,
            description='Tri an khach hang than thiet'
        ),
        Promotion(
            code='BDAY30',
            start_date=datetime(2026, 1, 1, 0, 0, 0),
            expire_date=datetime(2026, 2, 1, 23, 59, 59),
            promotion_type=PromotionType.COUPON,
            availability_count=2,
            value=0.30,
            max_discount_amount=250000,
            min_order_value=600000,
            description='Sinh nhat giam 30%'
        ),
        Promotion(
            code='SHIP50K',
            start_date=datetime(2026, 3, 1, 0, 0, 0),
            expire_date=datetime(2026, 12, 31, 23, 59, 59),
            promotion_type=PromotionType.VOUCHER,
            availability_count=5,
            value=50000,
            max_discount_amount=None,
            min_order_value=0,
            description='Voucher 50k cho moi don'
        ),
        Promotion(
            code='LESS100K',
            start_date=datetime(2026, 2, 15, 0, 0, 0),
            expire_date=datetime(2026, 9, 30, 23, 59, 59),
            promotion_type=PromotionType.VOUCHER,
            availability_count=2,
            value=100000,
            max_discount_amount=None,
            min_order_value=300000,
            description='Giam truc tiep 100k'
        ),
        Promotion(
            code='LESS150K',
            start_date=datetime(2026, 3, 20, 0, 0, 0),
            expire_date=datetime(2026, 10, 31, 23, 59, 59),
            promotion_type=PromotionType.VOUCHER,
            availability_count=2,
            value=150000,
            max_discount_amount=None,
            min_order_value=500000,
            description='Don tren 500k giam 150k'
        ),
        Promotion(
            code='LESS200K',
            start_date=datetime(2026, 4, 1, 0, 0, 0),
            expire_date=datetime(2026, 10, 30, 23, 59, 59),
            promotion_type=PromotionType.VOUCHER,
            availability_count=5,
            value=200000,
            max_discount_amount=None,
            min_order_value=700000,
            description='Khuyen mai quy 2 giam 200k'
        ),
        Promotion(
            code='BIG300K',
            start_date=datetime(2026, 2, 1, 0, 0, 0),
            expire_date=datetime(2026, 12, 31, 23, 59, 59),
            promotion_type=PromotionType.VOUCHER,
            availability_count=50,
            value=300000,
            max_discount_amount=None,
            min_order_value=900000,
            description='Voucher gia tri lon 300k'
        ),
        Promotion(
            code='NIGHT80K',
            start_date=datetime(2026, 3, 1, 0, 0, 0),
            expire_date=datetime(2026, 11, 30, 23, 59, 59),
            promotion_type=PromotionType.VOUCHER,
            availability_count=130,
            value=80000,
            max_discount_amount=None,
            min_order_value=250000,
            description='Khung gio toi giam 80k'
        ),
        Promotion(
            code='HOLIDAY120',
            start_date=datetime(2026, 4, 10, 0, 0, 0),
            expire_date=datetime(2026, 4, 11, 23, 59, 59),
            promotion_type=PromotionType.VOUCHER,
            availability_count=100,
            value=120000,
            max_discount_amount=None,
            min_order_value=400000,
            description='Le tet giam 120k'
        ),
        Promotion(
            code='PAYDAY90K',
            start_date=datetime(2026, 8, 25, 0, 0, 0),
            expire_date=datetime(2026, 8, 31, 23, 59, 59),
            promotion_type=PromotionType.VOUCHER,
            availability_count=115,
            value=90000,
            max_discount_amount=None,
            min_order_value=350000,
            description='Ngay luong giam 90k'
        ),
        Promotion(
            code='FAST60K',
            start_date=datetime(2026, 3, 1, 0, 0, 0),
            expire_date=datetime(2026, 4, 1, 23, 59, 59),
            promotion_type=PromotionType.VOUCHER,
            availability_count=2,
            value=60000,
            max_discount_amount=None,
            min_order_value=150000,
            description='Voucher nhanh 60k'
        ),
        Promotion(
            code='FREEDAY110',
            start_date=datetime(2026, 6, 1, 0, 0, 0),
            expire_date=datetime(2026, 12, 31, 23, 59, 59),
            promotion_type=PromotionType.VOUCHER,
            availability_count=10,
            value=110000,
            max_discount_amount=None,
            min_order_value=380000,
            description='Ngay dac biet giam 110k'
        ),
    ]
    test_session.add_all(promotions)
    test_session.commit()
    return promotions
    

@pytest.fixture
def sample_user(test_session):
    password_hash = hashlib.md5('password123'.encode("utf-8")).hexdigest()
    user1 = User(full_name='Nguyen Van A', phone_number='123456789', role='CUSTOMER', password_hash=password_hash)
    user2 = User(full_name='Nguyen Van B', phone_number='13572468', role='CUSTOMER', password_hash=password_hash)
    user3 = User(full_name='Nguyen Van C', phone_number='24681357', role='CUSTOMER', password_hash=password_hash)
    admin = User(full_name='Admin User', phone_number='987654321', role='ADMIN', password_hash=password_hash)
    test_session.add(user1)
    test_session.add(user2)
    test_session.add(user3)
    test_session.add(admin)
    test_session.commit()
    return [user1, user2, user3, admin]


@pytest.fixture
def sample_order(test_session, sample_user, sample_promotion):
    user1 = sample_user[0]
    user2 = sample_user[1]
    user3 = sample_user[2]

    save15 = sample_promotion[1]
    flash20 = sample_promotion[2]
    bday30 = sample_promotion[9]
    less100k = sample_promotion[11]
    less150k = sample_promotion[12]
    fast60k = sample_promotion[18]

    orders = [
        create_order(
            customer_id=user1.id,
            sub_total_amount=400000,
            discount_amount=50000,
            final_amount=350000,
            promotion_id=save15.id,
        ),
        create_order(
            customer_id=user1.id,
            sub_total_amount=400000,
            discount_amount=50000,
            final_amount=350000,
            promotion_id=save15.id,
        ),
        create_order(
            customer_id=user2.id,
            sub_total_amount=600000,
            discount_amount=100000,
            final_amount=500000,
            promotion_id=flash20.id,
        ),
        create_order(
            customer_id=user2.id,
            sub_total_amount=600000,
            discount_amount=100000,
            final_amount=500000,
            promotion_id=flash20.id,
        ),
        create_order(
            customer_id=user3.id,
            sub_total_amount=700000,
            discount_amount=150000,
            final_amount=550000,
            promotion_id=bday30.id,
        ),
        create_order(
            customer_id=user3.id,
            sub_total_amount=700000,
            discount_amount=150000,
            final_amount=550000,
            promotion_id=bday30.id,
        ),
        create_order(
            customer_id=user1.id,
            sub_total_amount=400000,
            discount_amount=100000,
            final_amount=300000,
            promotion_id=less100k.id,
        ),
        create_order(
            customer_id=user1.id,
            sub_total_amount=400000,
            discount_amount=100000,
            final_amount=300000,
            promotion_id=less100k.id,
        ),
        create_order(
            customer_id=user2.id,
            sub_total_amount=600000,
            discount_amount=150000,
            final_amount=450000,
            promotion_id=less150k.id,
        ),
        create_order(
            customer_id=user2.id,
            sub_total_amount=600000,
            discount_amount=150000,
            final_amount=450000,
            promotion_id=less150k.id,
        ),
        create_order(
            customer_id=user3.id,
            sub_total_amount=250000,
            discount_amount=60000,
            final_amount=190000,
            promotion_id=fast60k.id,
        ),
        create_order(
            customer_id=user3.id,
            sub_total_amount=250000,
            discount_amount=60000,
            final_amount=190000,
            promotion_id=fast60k.id,
        ),
    ]

    return orders


@pytest.fixture
def sample_user_promotion_usage(test_session, sample_user, sample_promotion, sample_order):
    user1 = sample_user[0]
    user2 = sample_user[1]
    user3 = sample_user[2]

    save15 = sample_promotion[1]
    flash20 = sample_promotion[2]
    bday30 = sample_promotion[9]
    less100k = sample_promotion[11]
    less150k = sample_promotion[12]
    fast60k = sample_promotion[18]

    usages = [
        UserPromotionUsage(user_id=user1.id, promotion_id=save15.id, usage_count=2),
        UserPromotionUsage(user_id=user2.id, promotion_id=flash20.id, usage_count=2),
        UserPromotionUsage(user_id=user3.id, promotion_id=bday30.id, usage_count=2),
        UserPromotionUsage(user_id=user1.id, promotion_id=less100k.id, usage_count=2),
        UserPromotionUsage(user_id=user2.id, promotion_id=less150k.id, usage_count=2),
        UserPromotionUsage(user_id=user3.id, promotion_id=fast60k.id, usage_count=2),
    ]

    test_session.add_all(usages)
    test_session.commit()

    return usages