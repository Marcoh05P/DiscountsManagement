import hashlib
from datetime import datetime

from DiscountsManagementApp.models import User, UserRole, Promotion, Order, UserPromotionUsage
from DiscountsManagementApp import db, app


def get_user_by_phone_number(phone_number):
    return User.query.filter_by(phone_number=phone_number).first()

def auth_user(phone_number, password):
    if not phone_number or not password:
        return None

    password_hash = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.phone_number == phone_number.strip(),
                            User.password_hash == password_hash).first()
    
def check_phone_number_exists(phone_number):
    return User.query.filter_by(phone_number=phone_number).first() is not None

def add_user(phone_number, password, full_name, role=UserRole.CUSTOMER):
    password_hash = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(phone_number=phone_number,
                password_hash=password_hash,
                full_name=full_name,
                role=role)
    db.session.add(user)
    db.session.commit()


def create_order(customer_id, sub_total_amount, discount_amount, final_amount, promotion_id=None):
    order = Order(customer_id=customer_id,
                  promotion_id=promotion_id,
                  sub_total_amount=sub_total_amount,
                  discount_amount=discount_amount,
                  final_amount=final_amount)
    db.session.add(order)
    db.session.commit()
    return order


def update_order(order_id, promotion_id=None, discount_amount=None, final_amount=None,
                 status=None):
    order = Order.query.get(order_id)
    if not order:
        return None

    if promotion_id is not None:
        order.promotion_id = promotion_id
    if discount_amount is not None:
        order.discount_amount = discount_amount
    if final_amount is not None:
        order.final_amount = final_amount
    if status is not None:
        order.status = status

    db.session.commit()
    return order


def get_promotion_by_code(code):
    return Promotion.query.filter(Promotion.code.__eq__(code.strip())).first()


def get_promotions(code=None, expired=False, ptype=None, order_value=None, is_available=True, page=None):
    query = Promotion.query

    if code:
        query = query.filter(Promotion.code.__eq__(code.strip()))

    if expired:
        query = query.filter(Promotion.expire_date < datetime.now())

    if ptype:
        query = query.filter(Promotion.promotion_type == ptype)

    if order_value and order_value > 0:
        query = query.filter((Promotion.min_order_value is None) or (Promotion.min_order_value <= order_value))

    if is_available:
        query = query.filter(Promotion.availability_count > 0)

    if not page:
        page = 1
    return query.paginate(page=page, per_page=app.config['PAGE_SIZE'])


def create_user_promotion_usage(user_id, promotion_id):
    usage = UserPromotionUsage(user_id=user_id, promotion_id=promotion_id, usage_count=1)
    db.session.add(usage)
    db.session.commit()
    return usage


def get_user_promotion_usage(user_id, promotion_id):
    return UserPromotionUsage.query.filter_by(user_id=user_id, promotion_id=promotion_id).first()
