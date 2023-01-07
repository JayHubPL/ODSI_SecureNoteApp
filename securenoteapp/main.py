from flask import Blueprint, render_template, request, current_app, redirect, url_for, flash, session
from flask_login import login_required, current_user
from sqlalchemy.sql import text
import markdown
from .models import Note
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    notes = Note.query.filter_by(owner_id = current_user.id).all()
    current_app.logger.debug('%s', notes)
    
    return render_template('profile.html', name=current_user.name, notes=notes)

@main.route('/note')
@login_required
def note_create():
    if 'wip_note_text' not in session:
        session['wip_note_text'] = ""
    current_app.logger.debug('%s', session['wip_note_text'])

    return render_template('new_note.html', note_text=session['wip_note_text'])

@main.route('/note', methods=['POST'])
@login_required
def note_post():
    title = request.form['title']
    content = request.form['content']

    if not title:
        flash("Title cannot be empty")
        session['wip_note_text'] = content
        return redirect(url_for('main.note_create'))
    else:
        session['wip_note_text'] = ""

    new_note = Note(owner_id=current_user.id, title=title, content=content)

    db.session.add(new_note)
    db.session.commit()

    return redirect(url_for('main.profile'))

@main.route('/note/<note_id>')
@login_required
def note_show(note_id):
    note = Note.query.filter_by(id=note_id).one()
    current_app.logger.debug('%s', note.content)

    if note is None or note.owner_id is not current_user.id:
        flash("Invalid note_id")
        return redirect(url_for('main.profile'))

    rendered = markdown.markdown(note.content)

    return render_template('display_note.html', rendered=rendered)
