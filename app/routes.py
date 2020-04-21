from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app
from sqlalchemy import func
from datetime import datetime
from app.models import User

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

####Authentication Routes####
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from app import db
from app.forms import RegistrationForm

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (func.upper(User.username) == func.upper(form.login_name.data))|
            (func.upper(User.email) == func.upper(form.login_name.data))
        ).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username, email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc !='':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, first_name=form.first_name.data, last_name=form.last_name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form =form)


####Main Routes####
@app.route('/')
@app.route('/index')
@login_required
def index():
    projects = [
        {
            'name': 'Project 1',
            'created_by': {'first_name': 'Julian'}
        },
        {
            'name': 'Project 2',
            'created_by': {'first_name': 'Susan'}
        }
    ]
    return render_template('index.html', title='Home', projects=projects)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username = username).first_or_404()
    projects = [
        {
            'name': 'Project 1 the user is working on',
            'created_by': {'first_name': 'Julian'}
        },
        {
            'name': 'Project 2 the user is working on',
            'created_by': {'first_name': 'Susan'}
        }
    ]
    return render_template('user.html', user=user, projects=projects)


from app.forms import EditProfileForm

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)
