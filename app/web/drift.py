from flask import render_template, flash, redirect, url_for, request
from sqlalchemy import or_, desc

from app.forms.drift import DriftForm
from app.lib.email import send_mail
from app.lib.enums import PendingStatus
from app.models.base import db
from app.models.drift import Drift
from app.models.gift import Gift
from app.models.user import User
from app.models.wish import Wish
from app.view_models.drift import DriftCollection
from app.view_models.user import UsersSummary
from . import web
from flask_login import login_required, current_user


@web.route('/pending/')
@login_required
def pending():
    drifts = Drift.query.filter(or_(Drift.requester_id==current_user.id, Drift.gifter_id), Drift.status == 1).order_by(
        desc(Drift.create_time)).all()

    view_models = DriftCollection(drifts, current_user.id)

    return render_template('pending.html', drifts=view_models.data)

@web.route('/drift/<int:gid>', methods=['GET', 'POST'])
@login_required
def send_drift(gid):
    gift = Gift.query.get_or_404(gid)
    if gift.is_myself_gift(current_user.id):
        return redirect(url_for('web.book_detail', isbn=gift.isbn))
    if not current_user.can_send_drift():
        return render_template('not_enough_beans.html', beans=current_user.beans)

    wtform = DriftForm(request.form)
    if request.method == 'POST' and wtform.validate():
        drift = Drift()
        drift.save_to_drift(wtform, gift, current_user.id, current_user.nickname)
        send_mail(gift.user.email, '有人想要您上传的图书: 《' + gift.book['title'] + '》', 'email/get_gift.html',
                  wisher=current_user, gift=gift)
        return redirect(url_for('web.pending'))
    user = User.query.filter_by(id=gift.uid).first_or_404()
    viewmodel = UsersSummary(user)
    return render_template('drift.html', gifter=viewmodel.first, user_beans=current_user.beans, form=wtform)


@web.route('/drift/<int:did>/reject')
@login_required
def reject_drift(did):
    drift = Drift.query.filter(
        Drift.id == did,
        Drift.gifter_id == current_user.id,
        Drift.status == 1).first_or_404()

    with db.auto_commit():
        drift.pending = PendingStatus.Reject
        requester = User.query.get(drift.requester_id)
        # requester = User.query.filter(User.id == drift.requester_id).first_or_404()

        requester.beans += 1
        db.session.add(drift)
        db.session.add(requester)
        flash('已经成功拒绝一条鱼漂请求')

    return redirect(url_for('web.pending'))


@web.route('/drift/<int:did>/redraw')
@login_required
def redraw_drift(did):
    with db.auto_commit():
        drift = Drift.query.filter(Drift.id == did, Drift.requester_id == current_user.id,
                                   Drift._pending == PendingStatus.Waiting.value, Drift.status == 1).first_or_404()
        drift.pending = PendingStatus.Redraw
        current_user.beans += 1
        db.session.add(drift)
        flash('已经成功撤销一条鱼漂请求')
    return redirect(url_for('web.pending'))


@web.route('/drift/<int:did>/mailed')
@login_required
def mailed_drift(did):
    with db.auto_commit():
        drift = Drift.query.filter(Drift.id == did,
                                   Drift.gifter_id == current_user.id,
                                   Drift._pending == PendingStatus.Waiting.value,
                                   Drift.status == 1).first_or_404()

        requester = User.query.get(drift.requester_id)
        drift.pending = PendingStatus.Success
        current_user.beans += 1
        requester.receive_counter += 1
        current_user.send_counter += 1
        gift = Gift.query.get_or_404(drift.gift_id)
        gift.launched = True
        wish = Wish.query.filter(Wish.isbn == drift.isbn,
                                 Wish.uid == drift.requester_id,
                                 Wish.launched == False,
                                 Drift.status == 1).first()
        if wish:
            wish.launched = True
            db.session.add(wish)

        db.session.add(requester)
        db.session.add(drift)
        db.session.add(gift)
        flash('已经成功邮寄一条鱼漂了~感谢您的公益风险~')
    return redirect(url_for('web.pending'))

