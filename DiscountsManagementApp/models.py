from flask_login import UserMixin
from sqlalchemy import Column, Double, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship, backref
from DiscountsManagementApp import db, app
from enum import Enum as EnumBase
from datetime import datetime


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, default=True)
    
class UserRole(EnumBase):
    ADMIN = 'ADMIN'
    CUSTOMER = 'CUSTOMER'

class PromotionType(EnumBase):
    COUPON = 'COUPON'
    VOUCHER = 'VOUCHER'
    
    def __str__(self):
        return self.value

    def get_discount_calculator(self):
        calculators = {
            PromotionType.COUPON: lambda sub_total, max_discount, value: min(sub_total * value, max_discount if max_discount else sub_total),
            PromotionType.VOUCHER: lambda sub_total, max_discount, value: value
        }
        return calculators[self]


class OrderStatus(EnumBase):
    PENDING = 'PENDING'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'
    
class User(BaseModel, UserMixin):
    __tablename__ = 'users'
    phone_number = Column(String(10), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CUSTOMER)
    
class Promotion(BaseModel):
    __tablename__ = 'promotions'
    code = Column(String(10), unique=True, nullable=False, index=True)
    start_date = Column(DateTime, default=datetime.now)
    expire_date = Column(DateTime, nullable=False)
    
    promotion_type = Column(Enum(PromotionType), nullable=False)
    availability_count = Column(Integer, nullable=False)
    value = Column(Double, nullable=False)
    max_discount_amount = Column(Double, nullable=True)
    min_order_value = Column(Double, nullable=True, default=0.0)

    description = Column(String(255))
    
    
class Order(BaseModel):
    __tablename__ = 'orders'
    customer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    promotion_id = Column(Integer, ForeignKey('promotions.id'))
    created_date = Column(DateTime, default=datetime.now)
    
    sub_total_amount = Column(Double, nullable=False)
    discount_amount = Column(Double, default=0.0)
    final_amount = Column(Double, nullable=False)
    
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    
    user = relationship('User', foreign_keys=[customer_id], backref=backref('orders', lazy=True))
    promotion = relationship('Promotion', foreign_keys=[promotion_id], backref=backref('orders', lazy=True))
    
class UserPromotionUsage(BaseModel):
    __tablename__ = 'user_promotion_usages'
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    promotion_id = Column(Integer, ForeignKey('promotions.id'), nullable=False)
    usage_count = Column(Integer, default=1)
    
    user = relationship('User', foreign_keys=[user_id], backref=backref('user_promotion_usages', lazy=True))
    promotion = relationship('Promotion', foreign_keys=[promotion_id], backref=backref('user_promotion_usages', lazy=True))
