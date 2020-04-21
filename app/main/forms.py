from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo, Length
from sqlalchemy import func
from app.models import User


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

