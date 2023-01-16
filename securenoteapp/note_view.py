import re
import uuid

import markdown
from bleach import Cleaner
from flask import (Blueprint, Response, current_app, flash, redirect,
                   render_template, request, session, url_for)
from flask_login import current_user, login_required
from werkzeug.security import safe_join
from werkzeug.utils import secure_filename

from . import db
from .crypto import check_note_password, decrypt_note, encrypt_note
from .models import Note
from .utils import (check_password_strength,
                    get_password_strength_flash_message, get_validated_note,
                    is_file_allowed)

note_view = Blueprint('note_view', __name__, url_prefix='/note')

cleaner = Cleaner(
    tags=['h1', 'h2', 'h3', 'h4', 'h5', 'a',
          'strong', 'em', 'p', 'img'],
    attributes={'a': ['href'], 'img': ['src']}
)


@note_view.route('/')
@login_required
def note_create():
    return render_template('new_note.html', note_title=session['wip_title'], note_text=session['wip_content'])


@note_view.route('/', methods=['POST'])
@login_required
def note_post():
    title = request.form['title']
    content = request.form['content']

    session['wip_title'] = title
    session['wip_content'] = content

    if not title:
        flash("Title cannot be empty")
        return redirect(url_for('note_view.note_create'))

    files_to_save = dict()
    uploads = request.files.getlist('photos')
    for file in uploads:
        if not file:
            continue
        filename = secure_filename(file.filename)
        if is_file_allowed(filename):
            regex = r'!\[.*\]\(.*' + re.escape(filename) + r'.*\)'
            if re.search(regex, content) is None:
                flash('Remove unused pictures from uploads')
                return redirect(url_for('note_view.note_create'))
            file_uuid = str(uuid.uuid4())
            content = content.replace(filename, url_for(
                'main.uploaded_file', uuid=file_uuid))
            files_to_save[file_uuid] = file
        else:
            flash('You can only upload pictures')
            return redirect(url_for('note_view.note_create'))
    for file_uuid, file in files_to_save.items():
        file.save(safe_join(current_app.root_path,
                  current_app.config['UPLOAD_FOLDER'], file_uuid))

    if request.form['password']:
        password = request.form['password']
        pw_strength_info = check_password_strength(password)
        if not pw_strength_info['password_ok']:
            current_app.logger.debug('%s', pw_strength_info)
            flash(get_password_strength_flash_message(pw_strength_info))
            return redirect(url_for('note_view.note_create'))
        else:
            pwhash, encrypted_content = encrypt_note(content, password)
            new_note = Note(owner_id=current_user.id, title=title,
                            content=encrypted_content, is_encrypted=True, password=pwhash)
    else:
        new_note = Note(owner_id=current_user.id, title=title,
                        content=content, is_encrypted=False)

    db.session.add(new_note)
    db.session.commit()

    return redirect(url_for('main.profile'))


@note_view.route('/<note_id>')
@login_required
def note_show(note_id):
    note = get_validated_note(note_id)
    if isinstance(note, Response):
        return note

    if note.is_encrypted:
        return render_template('enter_note_password.html', form_action=url_for('note_view.validate_note_password', note_id=note_id), button_message="Decrypt note")
    else:
        rendered = cleaner.clean(markdown.markdown(note.content))
        current_app.logger.debug('Rendered %s', rendered)
        is_owner = note.owner_id == current_user.id
        return render_template('display_note.html', note=note, rendered=rendered, is_owner=is_owner)


@note_view.route('/<note_id>', methods=['POST'])
@login_required
def validate_note_password(note_id):
    note = get_validated_note(note_id, True)
    if isinstance(note, Response):
        return note

    password = request.form['password']

    if check_note_password(password, note.password):
        decrypted = decrypt_note(note.content, note.password)
        rendered = markdown.markdown(decrypted)
        return render_template('display_note.html', note=note, rendered=rendered, is_owner=True)
    else:
        flash("Invalid password")
        return redirect(url_for('note_view.note_show', note_id=note_id))
