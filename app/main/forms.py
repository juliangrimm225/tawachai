from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo, Length
from sqlalchemy import func
from app.models import User
from flask import request


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data.upper() != self.original_username.upper():
            user = User.query.filter(
                func.upper(User.username)==func.upper(self.username.data)).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class ProjectForm(FlaskForm):
    name = StringField('Create a new project!', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditProjectForm(FlaskForm):
    name = StringField('New Project Name')
    submit = SubmitField('Submit')

class NodeForm(FlaskForm):
    input_format = '%Y-%m-%dT%H:%M'
    name = StringField('New Node', validators=[DataRequired()])
#    end = DateTimeLocalField('Pick a Due Date (Format: '+ input_format, format = input_format)
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)


