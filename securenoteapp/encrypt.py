from flask import (Blueprint, Response, flash, redirect, render_template,
                   request, url_for)
from flask_login import login_required

from . import db
from .crypto import decrypt_note, encrypt_note
from .models import Note
from .utils import (check_password_strength,
                    get_password_strength_flash_message, get_validated_note)

encrypt = Blueprint('encrypt', __name__)


@encrypt.route('/change_encryption_status/<note_id>', methods=['POST'])
@login_required
def change_encryption_status(note_id):
    note = get_validated_note(note_id, must_own=True)
    if isinstance(note, Response):
        return note

    if note.is_encrypted:
        content_decrypted = decrypt_note(note.content, note.password)
        Note.query.filter_by(id=note.id).update(
            dict(is_encrypted=False, content=content_decrypted))
        db.session.commit()
        return redirect(url_for('main.profile'))
    else:
        return render_template('enter_note_password.html', form_action=url_for('encrypt.add_password', note_id=note_id), button_message="Add password")


@encrypt.route('/add_password/<note_id>', methods=['POST'])
@login_required
def add_password(note_id):
    note = get_validated_note(note_id, must_own=True)
    if isinstance(note, Response):
        return note

    if note.is_encrypted:
        flash('Note is already encrypted')
    else:
        password = request.form['password']
        pw_info = check_password_strength(password)
        if not pw_info['password_ok']:
            flash(get_password_strength_flash_message(pw_info))
            return redirect(url_for('encrypt.change_encryption_status', note_id=note_id))
        pwhash, encrypted_content = encrypt_note(note.content, password)
        Note.query.filter_by(id=note.id).update(
            dict(is_encrypted=True, content=encrypted_content, password=pwhash))
        db.session.commit()

    return redirect(url_for('main.profile'))
