from DiscountsManagementApp import app, db
from DiscountsManagementApp import index, models
from DiscountsManagementApp import admin
from flask_login import current_user

if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()

    #     import hashlib
    #     u = models.User(phone_number='0706823664', password_hash=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()), full_name="Admin User", role=models.UserRole.ADMIN)
    #     db.session.add(u)
    #     db.session.commit()
    #     print("Admin user created with phone number '0706823664' and password '123456'")
    index.register_routes(app)
    app.run(debug=True)