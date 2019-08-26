from sqlalchemy import Column, Integer, ForeignKey, Boolean, String, desc, func
from sqlalchemy.orm import relationship
from app.models.base import Base, db
from flask import current_app

from app.spider.yushu_book import YuShuBook


class Gift(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    # ???
    user = relationship('User')
    uid = Column(Integer, ForeignKey('user.id'))
    isbn = Column(String(15), nullable=False)
    launched = Column(Boolean, default=False)

    @property
    def book(self):
        yushu_book = YuShuBook()
        yushu_book.isbnSearch(self.isbn)
        return yushu_book.first

    @classmethod
    def recent(cls):
        gifts = Gift.query.filter_by(launched=False).group_by(Gift.isbn).order_by(
            desc(Gift.create_time)).distinct().limit(current_app.config['RECENT_BOOK_COUNT']).all()

        return gifts

    @classmethod
    def get_user_gifts(cls, id):
        gifts = Gift.query.filter_by(uid=id, launched=False).order_by(desc(Gift.create_time)).all()
        return gifts

    @classmethod
    def get_wish_counts(cls, isbn_list):
        from app.models.wish import Wish
        count_list = db.session.query(func.count(Wish.id), Wish.isbn).filter(Wish.launched == False,
                                                                             Wish.isbn.in_(isbn_list),
                                                                             Wish.status == 1).group_by(Wish.isbn).all()
        wish_count = [{'count': res[0], 'isbn': res[1]} for res in count_list]
        return wish_count

    def is_myself_gift(self, uid):
        return True if uid == self.uid else False
