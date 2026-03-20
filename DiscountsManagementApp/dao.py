import hashlib
from DiscountsManagementApp.models import User

def auth_user(phone_number, password):
    password_hash = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.phone_number==phone_number,
                            User.password_hash==password_hash).first()