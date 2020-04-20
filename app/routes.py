from flask import render_template, flash, redirect, url_for
from app import app

####Authentication Routes####
from app.forms import LoginForm

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for {}, remember_me={}'.format(
            form.email.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form = form)

####Main Routes####
@app.route('/')
@app.route('/index')
def index():
    user = {'first_name': 'Julian'}
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
    return render_template('index.html', title='Home', user=user, projects=projects)

