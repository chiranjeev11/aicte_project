
from flask_wtf  import FlaskForm, Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User
from flask_wtf.file import FileAllowed

class LoginForm(FlaskForm):

	email = StringField('Email',validators=[DataRequired()])

	password = PasswordField('Password', validators=[DataRequired()])

	remember_me = BooleanField('Remember Me')

	submit = SubmitField('Sign In')

class EditProfileForm(FlaskForm):

	name = StringField('Name', validators=[DataRequired()])

	email = StringField('Email', validators=[DataRequired(), Email()])

	submit = SubmitField('Edit Profile')


class ChangePasswordForm(FlaskForm):

	old_password = StringField('Old Password', validators=[DataRequired()])

	new_password = StringField('New Password', validators=[DataRequired()])

	confirm_new_password = StringField('Confirm new password', validators=[DataRequired()])

	submit = SubmitField('Change Password')


class RegistrationForm(FlaskForm):

	name = StringField('Name', validators=[DataRequired()])

	email = StringField('Email', validators=[DataRequired(), Email()])

	password = PasswordField('Password', validators=[DataRequired()])

	password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])

	submit = SubmitField('Register')

	def validate_email(self, email):

		user = User.query.filter_by(email=email.data).first()

		if user is not None:

			raise ValidationError('Please use a different email address.')