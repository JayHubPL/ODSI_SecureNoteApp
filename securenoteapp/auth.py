from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from .utils import check_password_strength, generate_flash_msg
from . import db
import re

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email').strip()
    password = request.form.get('password')

    if not validateEmail(email):
        flash('Email is invalid.')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    login_user(user)
    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email').strip()
    name = request.form.get('name').strip()
    password = request.form.get('password')

    if not validateEmail(email):
        flash('Email is invalid.')
        return redirect(url_for('auth.signup'))

    user = User.query.filter_by(email=email).first()
    if user:
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    if not name:
        flash('Name cannot be empty.')
        return redirect(url_for('auth.signup'))

    pw_info = check_password_strength(password)
    if not pw_info['password_ok']:
        flash(generate_flash_msg(pw_info))
        return redirect(url_for('auth.signup'))
    
    password_hash = generate_password_hash(password, method='pbkdf2:sha512')
    new_user = User(email=email, name=name, password=password_hash)

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

def validateEmail(email: str):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.fullmatch(email_regex, email) is not None
    