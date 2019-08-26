from flask_login import current_user

from app.models.user import User
from app.view_models.user import UserSummary
from . import web
from app.models.gift import Gift
from app.view_models.book import BookViewModel
from flask import render_template


@web.route('/')
def index():
    recent_gifts = Gift.recent()
    books = [BookViewModel(gift.book) for gift in recent_gifts]
    return render_template('index.html', recent=books)


@web.route('/personal')
def personal_center():
    user = User.query.get_or_404(current_user.id)
    view_model = UserSummary(user)
    return render_template('personal.html', user=view_model)
