from flask import render_template, flash, redirect, url_for, request, current_app
from werkzeug.urls import url_parse
from flask_login import current_user, login_required
from sqlalchemy import func
from datetime import datetime
from app.models import User, Project
from app import db
from app.main.forms import EditProfileForm, ProjectForm
from app.main import bp
from flask import g
from app.main.forms import SearchForm

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()


@bp.route('/',methods=['GET','POST'])
@bp.route('/index', methods=['GET','POST'])
@login_required
def index():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(name=form.name.data, created_by=current_user)
        db.session.add(project)
        db.session.commit()
        flash('Added a new project.')
        return redirect(url_for('main.index'))
    page =request.args.get('page', 1, type=int)
    projects = Project.query.filter_by(created_by = current_user).order_by(Project.timestamp.desc()).paginate(
        page, current_app.config['PROJECTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=projects.next_num) \
        if projects.has_next else None
    prev_url = url_for('main.index', page=projects.prev_num) \
        if projects.has_prev else None
    return render_template('index.html', title='Home', form=form, projects=projects.items, next_url=next_url, prev_url=prev_url)

@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    projects = Project.query.order_by(Project.timestamp.desc()).paginate(page, current_app.config['PROJECTS_PER_PAGE'], False)

    next_url = url_for('main.explore', page=projects.next_num) \
        if projects.has_next else None
    prev_url = url_for('main.explore', page=projects.prev_num) \
        if projects.has_prev else None
    return render_template('index.html', title = 'Explore', projects=projects.items, next_url=next_url, prev_url=prev_url)

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username = username).first_or_404()
    page = request.args.get('page', 1, type=int)
    projects = Project.query.filter_by(created_by = user).order_by(Project.timestamp.desc()).paginate(page, current_app.config['PROJECTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=projects.next_num) \
        if projects.has_next else None
    prev_url = url_for('main.user', username=user.username, page=projects.prev_num) \
        if projects.has_prev else None
    return render_template('user.html', user=user, projects=projects.items, next_url=next_url, prev_url=prev_url)



@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    projects, total = Project.search(g.search_form.q.data, page,
        current_app.config['PROJECTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page= page +1) \
        if total > page * current_app.config['PROJECTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page = page -1) \
        if page > 1 else None
    return render_template('search.html', title ='Search', projects=projects, next_url=next_url, prev_url=prev_url)
    
