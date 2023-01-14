from flask_login import current_user
from math import log2
import re
from .crypto import PASSWORD_MIN_LEN
from . import db
from .models import Share

def check_password_strength(password):
    # calculating the length
    length_error = len(password) < PASSWORD_MIN_LEN
    # searching for digits
    digit_error = re.search(r"\d", password) is None
    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None
    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None
    # searching for symbols
    symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None
    # high enough entropy
    entropy_error = entropy(password) < 3
    # overall result
    password_ok = not ( length_error or digit_error or uppercase_error or lowercase_error or symbol_error or entropy_error)

    return {
        'password_ok' : password_ok,
        'length_error' : length_error,
        'digit_error' : digit_error,
        'uppercase_error' : uppercase_error,
        'lowercase_error' : lowercase_error,
        'symbol_error' : symbol_error,
        'entropy_error' : entropy_error
    }

def generate_flash_msg(pw_info):
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

from flask import flash, redirect, url_for, current_app
from flask_login import current_user
from .models import Note

def get_validated_note(note_id):
    if not note_id.isnumeric():
        flash('Invalid note_id')
        return redirect(url_for('main.profile'))

    note = Note.query.filter_by(id=note_id).first()
    current_app.logger.debug('%s', note.content)

    if note is None:
        flash("Invalid note_id")
        return redirect(url_for('main.profile'))
    
    if not check_view_permission(note):
        flash("You don't have permission to view this content")
        return redirect(url_for('main.profile'))

    return note

def check_view_permission(note):
    is_shared = Share.query.filter_by(note_id=note.id, viewer_id=current_user.id).first() is not None
    return is_shared or note.owner_id == current_user.id
