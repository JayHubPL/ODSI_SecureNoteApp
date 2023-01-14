import re

from flask import (Blueprint, Response, current_app, flash, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required

from . import db
from .models import Note, Share, User
from .utils import get_validated_note

share = Blueprint('share', __name__)


@share.route('/change_share_status/<note_id>')
@login_required
def change_share_status(note_id):
    note = get_validated_note(note_id)
    if isinstance(note, Response):
        return note

    if note.is_encrypted:
        flash('Note is encrypted and thus cannot be shared.')
        return redirect(url_for('main.profile'))

    if note.is_public:
        Note.query.filter_by(id=note.id).update(dict(is_public=False))
        db.session.commit()
        return redirect(url_for('main.profile'))
    else:
        return render_template('share_to.html', note_id=note_id)


@share.route('/change_share_status/<note_id>', methods=['POST'])
@login_required
def share_note(note_id):
    note = get_validated_note(note_id)
    if isinstance(note, Response):
        return note

    Share.query.filter_by(note_id=note.id).delete()

    emails = request.form['emails'].strip()
    for email in re.split(r',\s*', emails):
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash('There is no user with email {}'.format(email))
            db.session.flush()
            return redirect(url_for('share.change_share_status', note_id=note_id))
        share = Share(note_id=note.id, viewer_id=user.id)
        db.session.add(share)

    db.session.commit()
    return redirect(url_for('note_view.note_show', note_id=note_id))
