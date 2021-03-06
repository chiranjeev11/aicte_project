from flask import render_template, request, jsonify, redirect, url_for, flash, render_template
from google.api_core.gapic_v1 import method
from google.cloud import speech
# from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ChangePasswordForm, RequestResetForm, ResetPasswordForm
from app.models import Audio, User, User_Feedback
from flask_mail import Message
import os
import os.path
from os import path

from app import app, db, login, mail
import ffmpeg
import datetime
  
  



@app.route('/')
@login_required
def index():

	return render_template('index.html')

@app.route('/feedback')
@login_required
def feedback():

	users = User.query.all()

	users_list = []

	for user in users:
		for feedback in user.feedback:
			users_list.append({"name":user.name, "feedback_rating": feedback.rating, "feedback_message": feedback.message})

	return render_template('feedback.html', users=users_list)

@app.route('/audio')
@login_required
def audio():

	if current_user.name.lower()=="admin":

		users = User.query.all()

		transcripts = []

		for user in users:

			user_transcripts = user.audios.all()

			if user_transcripts:

				transcripts.append({"user":user.name, "user_transcripts":user_transcripts})
	else:

		transcripts = current_user.audios.all()

	return render_template('audio.html', transcripts=transcripts)

@app.route('/login', methods=['GET', 'POST'])
def login():

	if current_user.is_authenticated:

		return redirect(url_for('index'))

	form = LoginForm()

	if form.validate_on_submit():
		
		user = User.query.filter_by(email=form.email.data).first()


		if user is None or not user.check_password(form.password.data):

			flash('Invalid username or password')

			return redirect(url_for('login'))

		login_user(user, remember=form.remember_me.data)

		return redirect(url_for('index'))

	return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():

	if current_user.is_authenticated:

		return redirect(url_for('index'))

	form = RegistrationForm()

	if form.validate_on_submit():

		if form.name.data.lower()=="admin":
			flash('Please use a different name', 'error')
			return redirect(url_for('register'))

		user = User(name=form.name.data, email=form.email.data, dob=form.dob.data, gender=form.gender.data)

		user.set_password(form.password.data)

		db.session.add(user)

		db.session.commit()

		flash('Congratulations, you are now a registered user!')

		return redirect(url_for('login'))

	return render_template('register.html', title='Register', form=form)


@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	
	form = EditProfileForm()

	user = User.query.filter_by(email=current_user.email).first()

	if form.validate_on_submit():

		user.name = form.name.data

		user.email = form.email.data

		user.dob = form.dob.data

		user.gender = form.gender.data

		db.session.add(user)

		db.session.commit()

		flash('Details Edited Successfully', 'message')


	return render_template('edit_profile.html', form=form, user=user, gender_data = form.gender.data)

@app.route('/change_password', methods=['POST', 'GET'])
@login_required
def change_password():

	form = ChangePasswordForm()

	user = User.query.filter_by(name=current_user.name).first()

	if form.validate_on_submit():

		if user.check_password(form.old_password.data):

			if form.new_password.data == form.confirm_new_password.data:

				user.set_password(form.new_password.data)

				db.session.add(user)

				db.session.commit()

				flash('Your password has been updated', 'message')


			else:

				flash('new passwords does not match', 'error')

		else:

			flash('Enter correct password', 'error')

		return redirect(url_for('change_password'))



	return render_template('change_password.html', form=form)


@app.route('/logout')
@login_required
def logout():

	logout_user()

	return redirect(url_for('login'))


@app.route('/audioBlob', methods=['GET', 'POST'])
@login_required
def convertSpeechToText():

	data = request.files['audio_file'].read()


	if path.exists("app/static/audioFiles/audio.wav"):
		os.remove("app/static/audioFiles/audio.wav")

	with open("app/static/audioFiles/audio.wav", "wb") as file:
		file.write(data)

	if path.exists("app/static/audioFiles/audio_converted_wav.wav"):
		os.remove("app/static/audioFiles/audio_converted_wav.wav")

	wemp_to_wav_convertor("app/static/audioFiles/audio.wav", "app/static/audioFiles/audio_converted_wav.wav")
	
	# Instantiates a client
	client = speech.SpeechClient()

	with open("app{}".format("/static/audioFiles/audio_converted_wav.wav"), "rb") as file:
		content = file.read()


	

	# The name of the audio file to transcribe
	# gcs_uri = "gs://aicte/audio.wav"

	audio = speech.RecognitionAudio(content=content)

	config = speech.RecognitionConfig(
		encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
		# sample_rate_hertz=48000,
		# audio_channel_count = 2,
		language_code="en-IN",
		# model="video"
	)

	# # Detects speech in the audio file
	operation = client.long_running_recognize(config=config, audio=audio)

	# print(response)audio.wav



	response = operation.result(timeout=90)

	transcript = ""

	transcript_array = []

	for result in response.results:
		print("Transcript: {}".format(result.alternatives[0].transcript))
		transcript_array.append(result.alternatives[0].transcript)
		transcript+=result.alternatives[0].transcript

	return jsonify({"status":"success", "Transcript":transcript_array})

@app.route('/saveAudio', methods=['GET', 'POST'])
@login_required
def save_audio():

	transcript = request.form.get('transcript')

	current_time = datetime.datetime.now()

	audio_file_path = "/static/audioFiles/" + current_user.email + '_' + str(current_time) + '.wav'

	wemp_to_wav_convertor("app/static/audioFiles/audio.wav", "app{}".format(audio_file_path))

	audio_obj = Audio(audio_file_name=audio_file_path, transcript=transcript, user_id=current_user.id)

	db.session.add(audio_obj)

	db.session.commit()

	return jsonify({"status":"success"})

@app.route('/rateAudio', methods=['POST', 'GET'])
@login_required
def rate_audio():
	
	rating = request.form.get('rating')
	message = request.form.get('message')

	user_feedback = current_user.feedback

	if list(user_feedback):

		feedback=user_feedback[0]

		feedback.rating=rating

		feedback.message = message

	else:

		feedback = User_Feedback(user_id=current_user.id, rating=rating, message=message)

	db.session.add(feedback)

	db.session.commit()


	return jsonify({"status":"success"})

@app.route('/audio/delete', methods=['POST', 'GET'])
@login_required
def audio_delete():

	audio_id = request.args.get('id')

	audio = Audio.query.filter_by(id=int(audio_id)).first()

	audio_path = app.root_path+audio.audio_file_name

	os.remove(audio_path)

	db.session.delete(audio)

	db.session.commit()

	return jsonify({"status":"success"})

@app.route('/reset_password', methods=['POST', 'GET'])
def reset_request():

	if current_user.is_authenticated:

		return redirect(url_for('index'))

	form = RequestResetForm()

	if form.validate_on_submit():

		user = User.query.filter_by(email=form.email.data).first()

		send_reset_email(user)

		flash('An email has been sent with instructions to reset your password.')

		return redirect(url_for('login'))

	return render_template('reset_request.html', title='Reset Password' , form=form)

@app.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_token(token):

	if current_user.is_authenticated:

		return redirect(url_for('index'))

	user = User.verify_token(token)

	if user is None:

		flash('This is an invalid or expired token', 'warning')
		return redirect(url_for('reset_request'))

	form = ResetPasswordForm()

	if form.validate_on_submit():

		user.set_password(form.password.data)

		db.session.commit()

		flash('Your password as been updated. You are now able to login.')

		return redirect(url_for('login'))

	return render_template('reset_token.html', title='Reset Password', form=form)

def wemp_to_wav_convertor(input_file, output_file):

	stream = ffmpeg.input(input_file)
	stream = ffmpeg.output(stream, output_file)
	ffmpeg.run(stream)

def send_reset_email(user):
	
	token = user.get_reset_token()


	msg = Message('Pasword Reset Request', sender='noreply@demo.com', recipients=[user.email])


	msg.body = f'''To reset your password, visit here:
	{url_for('reset_token', token=token, _external=True)}
	'''

	mail.send(msg)