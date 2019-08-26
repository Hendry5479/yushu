from app.models.gift import Gift
from app.models.wish import Wish
from app.view_models.trade import TradeInfo
from . import web
from flask import request, render_template, flash
from flask_login import current_user
from app.forms.book import SearchForm
from app.lib.helper import isIsbnOrKey
from app.spider.yushu_book import YuShuBook
from app.view_models.book import BookCollection, BookViewModel

@web.route('/book/search/')
def search():
    wtforms = SearchForm(request.args)
    book = BookCollection()
    if wtforms.validate():
        q = wtforms.q.data.strip()
        page = wtforms.page.data

        is_isbn_or_key = isIsbnOrKey(q)

        yushu_book = YuShuBook()

        if is_isbn_or_key == 'isbn':
            yushu_book.isbnSearch(q)

        if is_isbn_or_key == 'key':
            yushu_book.keySearch(q, page)

        book.fill(yushu_book, q)

    else:
        flash('关键字错误，请重新输入关键字')

    return render_template('search_result.html', books=book)

@web.route('/book/<isbn>/detail')
def book_detail(isbn):
    has_in_gifts = False
    has_in_wishes = False

    if current_user.is_authenticated:
        if Gift.query.filter_by(uid=current_user.id, isbn=isbn).first():
            has_in_gifts = True
        if Wish.query.filter_by(uid=current_user.id, isbn=isbn).first():
            has_in_wishes = True

    yushu_book = YuShuBook()
    yushu_book.isbnSearch(isbn)
    book = BookViewModel(yushu_book.first)

    gifts = Gift.query.filter_by(isbn=isbn, launched=False).all()
    wishes = Wish.query.filter_by(isbn=isbn, launched=False).all()

    trade_gifts = TradeInfo(gifts)
    trade_wishes = TradeInfo(wishes)

    return render_template('book_detail.html', book=book, gifts=trade_gifts, wishes=trade_wishes,
                           has_in_gifts=has_in_gifts, has_in_wishes=has_in_wishes)





