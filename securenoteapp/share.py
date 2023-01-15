import re
import uuid

from flask import (Blueprint, Response, flash, redirect, render_template,
                   request, url_for, current_app)
from flask_login import login_required

from . import db
from .models import Note, Share, User
from .utils import get_validated_note

share = Blueprint('share', __name__)


@share.route('/change_share_status/<note_id>')
@login_required
def change_share_status(note_id):
    note = get_validated_note(note_id, must_own=True)
    if isinstance(note, Response):
        return note

    if note.is_encrypted:
        flash('Note is encrypted and thus cannot be shared.')
        return redirect(url_for('main.profile'))

    if note.is_public:
        Note.query.filter_by(id=note.id).update(
            dict(is_public=False, uuid=None))
        Share.query.filter_by(note_id=note.id).delete()
        db.session.commit()
        return redirect(url_for('note_view.note_show', note_id=note_id))
    else:
        return render_template('share_to.html', note_id=note_id)


@share.route('/change_share_status/<note_id>', methods=['POST'])
@login_required
def share_note(note_id):
    note = get_validated_note(note_id, must_own=True)
    if isinstance(note, Response):
        return note

    Share.query.filter_by(note_id=note.id).delete()

    emails = request.form['emails'].strip()
    if emails:
        for email in re.split(r',\s*', emails):
            user = User.query.filter_by(email=email).first()
            if user is None:
                flash('There is no user with email {}'.format(email))
                db.session.flush()
                return redirect(url_for('share.change_share_status', note_id=note_id))
            share = Share(note_id=note.id, viewer_id=user.id)
            db.session.add(share)
    else:
        note_uuid = str(uuid.uuid4())
        Note.query.filter_by(id=note.id).update(dict(uuid=note_uuid))

    Note.query.filter_by(id=note.id).update(dict(is_public=True))
    db.session.commit()
    return redirect(url_for('note_view.note_show', note_id=note_id))


@share.route('/public/<uuid>')
@login_required
def show_public_note(uuid):
    if not validateUuid(uuid):
        flash('Invalid UUID')
        return redirect(url_for('main.profile'))

    note = Note.query.filter(Note.uuid==uuid).first()
    current_app.logger.debug(note)

    if not note:
        flash('Invalid UUID')
        return redirect(url_for('main.profile'))

    return redirect(url_for('note_view.note_show', note_id=note.id))


def validateUuid(uuid):
    uuid_regex = re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}\Z', re.I)
    return uuid_regex.match(uuid) is not None