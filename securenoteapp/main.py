from flask import Blueprint, render_template, request, current_app, redirect, url_for, flash, session, send_from_directory
from flask_login import login_required, current_user
from sqlalchemy.sql import text
import markdown
from bleach import Cleaner
import re
import os
from werkzeug.utils import secure_filename
from .crypto import encrypt_note, decrypt_note, check_note_password
from .utils import check_password_strength, generate_flash_msg
from .models import Note
from . import db

main = Blueprint('main', __name__)

cleaner = Cleaner( \
    tags=['h1', 'h2', 'h3', 'h4', 'h5', 'a', 'strong', 'em', 'p', 'img', 'ul', 'li'], \
    attributes={ 'a': ['href'], 'img': ['src'] }
)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    notes = Note.query.filter_by(owner_id = current_user.id).all()
    current_app.logger.debug('%s', notes)

    session['wip_title'] = ""
    session['wip_content'] = ""
    
    return render_template('profile.html', name=current_user.name, notes=notes)

@main.route('/note')
@login_required
def note_create():
    if 'wip_title' not in session:
        session['wip_title'] = ""
    if 'wip_content' not in session:
        session['wip_content'] = ""

    return render_template('new_note.html', note_title=session['wip_title'], note_text=session['wip_content'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']

@main.route('/note', methods=['POST'])
@login_required
def note_post():
    title = request.form['title']
    content = request.form['content']

    session['wip_title'] = title
    session['wip_content'] = content

    if not title:
        flash("Title cannot be empty")
        return redirect(url_for('main.note_create'))

    for file in request.files.getlist('photos'):
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

    if request.form['password']:
        password = request.form['password']
        pw_strength_info = check_password_strength(password)
        if not pw_strength_info['password_ok']:
            current_app.logger.debug('%s', pw_strength_info)
            flash(generate_flash_msg(pw_strength_info))
            return redirect(url_for('main.note_create'))
        else:
            pwhash, encrypted_content = encrypt_note(content, password)
            new_note = Note(owner_id=current_user.id, title=title, content=encrypted_content, is_encrypted=True, password=pwhash)
    else:
        new_note = Note(owner_id=current_user.id, title=title, content=content, is_encrypted=False)

    db.session.add(new_note)
    db.session.commit()

    return redirect(url_for('main.profile'))

@main.route('/note/<note_id>')
@login_required
def note_show(note_id):
    if not note_id.isnumeric():
        flash('Invalid note_id')
        return redirect(url_for('main.profile'))

    note = Note.query.filter_by(id=note_id).one()
    current_app.logger.debug('%s', note.content)

    if note is None:
        flash("Invalid note_id")
        return redirect(url_for('main.profile'))
    
    if not check_view_permission(note):
        flash("You don't have permission to view this content")
        return redirect(url_for('main.profile'))

    if note.is_encrypted:
        return render_template('enter_note_password.html', note_id=note_id)
    else:
        rendered = cleaner.clean(markdown.markdown(note.content))
        for filename in re.findall(r'<img src="(.*)">', rendered):
            rendered = rendered.replace(filename, url_for('main.uploaded_file', filename=filename))
        current_app.logger.debug('Rendered %s', rendered)
        return render_template('display_note.html', title=note.title, rendered=rendered)

@main.route('/note/<note_id>', methods=['POST'])
@login_required
def validate_note_password(note_id):
    if not note_id.isnumeric():
        flash('Invalid note_id')
        return redirect(url_for('main.profile'))
        
    note = Note.query.filter_by(id=note_id).one()
    password = request.form['password']

    if check_note_password(password, note.password):
        decrypted = decrypt_note(note.content, note.password)
        rendered = markdown.markdown(decrypted)
        return render_template('display_note.html', title=note.title, rendered=rendered)
    else:
        flash("Invalid password")
        return redirect('main.note_show', note_id=note_id)

@main.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    current_app.logger.debug('Getting file: %s', filename)
    return send_from_directory(current_app.static_folder, filename) # TODO file is not found, why?

def check_view_permission(note):
    # TODO add share check
    return note.owner_id == current_user.id