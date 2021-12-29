
from flask_wtf  import FlaskForm, Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField
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
	
	dob = DateField('DOB', validators=[DataRequired()])

	gender = SelectField(u'Gender',  choices=[('none','select'), ('male', 'male'), ('female', 'female'), ('others', 'others')], validators=[DataRequired()])

	submit = SubmitField('Edit Profile')


class ChangePasswordForm(FlaskForm):

	old_password = StringField('Old Password', validators=[DataRequired()])

	new_password = StringField('New Password', validators=[DataRequired()])

	confirm_new_password = StringField('Confirm new password', validators=[DataRequired()])

	submit = SubmitField('Change Password')


class RegistrationForm(FlaskForm):

	name = StringField('Name', validators=[DataRequired()])

	email = StringField('Email', validators=[DataRequired(), Email()])

	dob = DateField('DOB', validators=[DataRequired()])

	gender = SelectField(u'Gender',  choices=[('1', 'male'), ('2', 'female'), ('3', 'others')], validators=[DataRequired()])

	password = PasswordField('Password', validators=[DataRequired()])

	password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])

	submit = SubmitField('Register')

	def validate_email(self, email):

		user = User.query.filter_by(email=email.data).first()

		if user is not None:

			raise ValidationError('Please use a different email address.')

class RequestResetForm(FlaskForm):

	email = StringField('Email', validators=[DataRequired(), Email()])

	submit = SubmitField('Request Password Reset')


	def validate_email(self, email):

		user = User.query.filter_by(email=email.data).first()

		if user is None:

			raise ValidationError('There is no account with this email. You must register first.')

class ResetPasswordForm(FlaskForm):

	password = PasswordField('Password', validators=[DataRequired()])

	password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])

	submit = SubmitField('Reset Password')