from flask_wtf import FlaskForm

from wtforms import StringField, TextAreaField, PasswordField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, ValidationError

from models import JournalEntry


def title_exists(form, field):
    if JournalEntry.select().where(JournalEntry.title**field.data).exists():
        raise ValidationError('An entry with that title already exists.')


class EntryForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        title_exists
    ])
    created_at = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    time = StringField('Time Spent', validators=[DataRequired()])
    entry = TextAreaField('What I Learned', validators=[DataRequired()])
    resources = TextAreaField('Resources to Remember (comma separated)')
    tags = StringField('Tags (comma separated)')


class EditEntryForm(FlaskForm):
    # Same as EntryForm but without DataRequired() for each field
    title = StringField('Title')
    created_at = DateField('Date', format='%Y-%m-%d')
    time = StringField('Time Spent')
    entry = TextAreaField('What I Learned')
    resources = TextAreaField('Resources to Remember (comma separated)')
    tags = StringField('Tags (comma separated)')


class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
