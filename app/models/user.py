from flask import current_app
from flask_login import UserMixin, current_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from math import floor

from app.lib.enums import PendingStatus
from app.models.drift import Drift
from app.models.gift import Gift
from app.models.wish import Wish
from app.spider.yushu_book import YuShuBook
from .base import Base, db
from sqlalchemy import Column, Integer, String, Boolean, Float
from werkzeug.security import generate_password_hash, check_password_hash
from app import login_manager
from app.lib.helper import isIsbnOrKey


class User(Base, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    nickname = Column(String(24), nullable=False)
    phone_number = Column(String(18), unique=True)
    _password = Column('password', String(256))
    email = Column(String(50), unique=True, nullable=False)
    confirmed = Column(Boolean, default=False)
    beans = Column(Float, default=0)
    send_counter = Column(Integer, default=0)
    receive_counter = Column(Integer, default=0)
    wx_open_id = Column(String(50))
    wx_name = Column(String(32))

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw):
        self._password = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self._password, raw)

    def can_save_to_list(self, isbn):
        if isIsbnOrKey(isbn) != 'isbn':
            return False

        yushu_book = YuShuBook()
        yushu_book.isbnSearch(isbn)
        if not yushu_book.first:
            return False

        gift = Gift.query.filter_by(isbn=isbn, uid=current_user.id, launched=False).first()
        wish = Wish.query.filter_by(isbn=isbn, uid=current_user.id, launched=False).first()
        if not gift and not wish:
            return True
        return False

    def generate_token(self, expiration=600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        token = s.dumps({'id': self.id}).decode('utf-8')
        return token

        # return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except Exception as e:
            return False

        uid = data.get('id')

        with db.auto_commit():
            user = User.query.get(uid)
            user.password = password
            db.session.add(user)
        return True

    @staticmethod
    def change_password(password):
        with db.auto_commit():
            user = User.query.get(current_user.id)
            user.password = password
            db.session.add(user)
        return True


    def can_send_drift(self):
        if self.beans < 1:
            return False

        success_gift_count = Gift.query.filter_by(uid=current_user.id, launched=True).count()
        success_drift_count = Drift.query.filter_by(requester_id=current_user.id, pending=PendingStatus.Success).count()

        return True if floor(success_drift_count / 2) >= success_drift_count else False





@login_manager.user_loader
def get_user(uid):
    return User.query.get(int(uid))