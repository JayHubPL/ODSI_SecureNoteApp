import re
from math import log2

from flask import current_app, flash, redirect, url_for
from flask_login import current_user

from . import db
from .crypto import PASSWORD_MIN_LEN
from .models import Note, Share


def check_password_strength(password):
    length_error = len(password) < PASSWORD_MIN_LEN
    digit_error = re.search(r"\d", password) is None
    uppercase_error = re.search(r"[A-Z]", password) is None
    lowercase_error = re.search(r"[a-z]", password) is None
    symbol_error = re.search(
        r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None
    entropy_error = entropy(password) < 3
    password_ok = not (
        length_error or digit_error or uppercase_error or lowercase_error or symbol_error or entropy_error)

    return {
        'password_ok': password_ok,
        'length_error': length_error,
        'digit_error': digit_error,
        'uppercase_error': uppercase_error,
        'lowercase_error': lowercase_error,
        'symbol_error': symbol_error,
        'entropy_error': entropy_error
    }


def get_password_strength_flash_message(pw_info):
    if pw_info['length_error']:
        msg = f'Password must have at least {PASSWORD_MIN_LEN} characters'
    elif pw_info['digit_error']:
        msg = 'Password must have at least one digit'
    elif pw_info['uppercase_error']:
        msg = 'Password must have at least one uppercase letter'
    elif pw_info['lowercase_error']:
        msg = 'Password must have at least one lowercase letter'
    elif pw_info['symbol_error']:
        msg = 'Password must have at least one special sign'
    else:
        msg = 'Password is too weak'
    return msg


def entropy(data):
    N = len(data)
    n = {}
    for b in data:
        if b in n:
            n[b] = n[b] + 1
        else:
            n[b] = 1
    entropy = 0
    for b in n.keys():
        p = n[b] / N
        entropy -= p * log2(p)
    return entropy


def get_validated_note(note_id, must_own=False):
    if not note_id.isnumeric():
        flash('Invalid note_id')
        return redirect(url_for('main.profile'))

    note = Note.query.filter_by(id=note_id).first()
    current_app.logger.debug('%s', note.content)

    if note is None:
        flash("Invalid note_id")
        return redirect(url_for('main.profile'))

    if not check_view_permission(note, must_own):
        flash("You don't have permission to view this content")
        return redirect(url_for('main.profile'))

    return note


def check_view_permission(note, must_own):
    is_owner = note.owner_id == current_user.id
    if must_own:
        return is_owner
    is_global = db.session.query(Note.query.filter(
        Note.id == note.id and Note.uuid is not None).exists()).scalar()
    is_shared = Share.query.filter_by(
        note_id=note.id, viewer_id=current_user.id).first() is not None
    return is_shared or is_owner or is_global


def is_file_allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']
