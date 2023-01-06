from flask import Blueprint, render_template, session, request, flash, redirect, url_for, current_app
from flask_login import login_required

note = Blueprint("note", __name__)

@note.route("/note")
@login_required
def new_note():
    current_app.logger.debug('%s', session['wip_note_text'])
    return render_template('new_note.html', note_text=session['wip_note_text'])

@note.route("/note", method=["POST"])
@login_required
def new_note():
    title = request.form['title']
    content = request.form['content']

    if not title:
        flash("Title cannot be empty")
        session['wip_note_text'] = content
        return redirect(url_for('main.profile'))
    else:
        session['wip_note_text'] = ""

    return render_template('new_note.html', note)