from flask import Blueprint, render_template, request, current_app, redirect, url_for, flash, session
from flask_login import login_required, current_user
from sqlalchemy.sql import text
from .models import Note
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    res = Note.query.filter_by(owner_id = current_user.id).all()
    current_app.logger.debug('%s', res)
    
    note_text = ""
    if session.get('wip_note_text'):
        note_text = session.get('wip_note_text')

    return render_template('profile.html', name=current_user.name, note_text=note_text)

@main.route('/note', methods=['POST'])
@login_required
def note_post():
    title = request.form['title']
    content = request.form['content']

    if not title:
        flash("Title cannot be empty")
        session['wip_note_text'] = content
        return redirect(url_for('main.profile'))
    else:
        session['wip_note_text'] = ""

    new_note = Note(owner_id=current_user.id, title=title, content=content)

    db.session.add(new_note)
    db.session.commit()

    return redirect(url_for('main.profile'))
