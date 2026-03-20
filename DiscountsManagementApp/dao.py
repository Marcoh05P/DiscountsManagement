import hashlib
from DiscountsManagementApp.models import User, UserRole
from DiscountsManagementApp import db

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