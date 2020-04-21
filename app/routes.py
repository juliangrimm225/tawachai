from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app
from sqlalchemy import func
from datetime import datetime
from app.models import User
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from app import db
from app.forms import EditProfileForm
from app.forms import RegistrationForm
from app.forms import ProjectForm
from app.models import Project
from app.forms import ResetPasswordRequestForm
from app.email import send_password_reset_email
from app.forms import ResetPasswordForm

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

####Authentication Routes####

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
@app.route('/',methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
@login_required
def index():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(name=form.name.data, created_by=current_user)
        db.session.add(project)
        db.session.commit()
        flash('Added a new project.')
        return redirect(url_for('index'))
    page =request.args.get('page', 1, type=int)
    projects = Project.query.filter_by(created_by = current_user).order_by(Project.timestamp.desc()).paginate(
        page, app.config['PROJECTS_PER_PAGE'], False)
    next_url = url_for('index', page=projects.next_num) \
        if projects.has_next else None
    prev_url = url_for('index', page=projects.prev_num) \
        if projects.has_prev else None
    return render_template('index.html', title='Home', form=form, projects=projects.items, next_url=next_url, prev_url=prev_url)

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    projects = Project.query.order_by(Project.timestamp.desc()).paginate(page, app.config['PROJECTS_PER_PAGE'], False)

    next_url = url_for('explore', page=projects.next_num) \
        if projects.has_next else None
    prev_url = url_for('explore', page=projects.prev_num) \
        if projects.has_prev else None
    return render_template('index.html', title = 'Explore', projects=projects.items, next_url=next_url, prev_url=prev_url)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username = username).first_or_404()
    page = request.args.get('page', 1, type=int)
    projects = Project.query.filter_by(created_by = user).order_by(Project.timestamp.desc()).paginate(page, app.config['PROJECTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=projects.next_num) \
        if projects.has_next else None
    prev_url = url_for('user', username=user.username, page=projects.prev_num) \
        if projects.has_prev else None
    return render_template('user.html', user=user, projects=projects.items, next_url=next_url, prev_url=prev_url)



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

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter(func.upper(User.email) == func.upper(form.email.data)).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password!')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title = 'Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form = form)
