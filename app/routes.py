from flask import render_template
from app import app

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

