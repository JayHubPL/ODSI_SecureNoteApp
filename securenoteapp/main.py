from flask import (Blueprint, current_app, render_template,
                   send_from_directory, session)
from flask_login import current_user, login_required

from . import db
from .models import Note, Share

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    notes = Note.query.filter_by(owner_id=current_user.id).all()
    shared_notes = db.session.query(Note).join(Share).filter(
        Share.viewer_id == current_user.id).all()
    current_app.logger.debug(shared_notes)

    session['wip_title'] = ""
    session['wip_content'] = ""

    return render_template('profile.html', name=current_user.name, notes=notes, shared_notes=shared_notes)


@main.route('/uploads/<uuid>')
@login_required
def uploaded_file(uuid):
    current_app.logger.debug('Getting file: %s', uuid)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], uuid)

@main.after_app_request
def add_security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response