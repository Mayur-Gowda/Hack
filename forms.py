from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, validators
from wtforms.validators import DataRequired, Length


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    phone = PasswordField('Phone', validators=[DataRequired()])
    message = StringField('Message', validators=[DataRequired()])
    submit = SubmitField('Submit')
