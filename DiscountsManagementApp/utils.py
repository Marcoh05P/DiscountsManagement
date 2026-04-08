from DiscountsManagementApp import db
from DiscountsManagementApp.dao import create_user_promotion_usage


def update_availability(user, promotion, user_promotion_usage=None, increment_usage=True):
    step = 1 if increment_usage else -1
    if user_promotion_usage and user_promotion_usage.usage_count + step > 0:
        user_promotion_usage.usage_count += step
    else:
        if increment_usage and promotion:
            create_user_promotion_usage(user.id, promotion.id)

    db.session.commit()


