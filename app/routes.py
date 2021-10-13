from flask import render_template, request, jsonify, redirect, url_for, flash, render_template
from google.api_core.gapic_v1 import method
from google.cloud import speech
# from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ChangePasswordForm
from app.models import Audio, User
import os
import os.path
from os import path

from app import app, db, login
import ffmpeg
import datetime
  
  



@app.route('/')
@login_required
def index():

	return render_template('index.html')

@app.route('/audio')
@login_required
def audio():

	if current_user.name=="admin":

		users = User.query.all()

		transcripts = []

		for user in users:

			user_transcripts = user.audios.all()

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

		if form.name.data=="admin":
			flash('Please use a different name', 'error')
			return redirect(url_for('register'))

		user = User(name=form.name.data, email=form.email.data)

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

	user = User.query.filter_by(name=current_user.name).first()

	if form.validate_on_submit():

		user.name = form.name.data

		user.email = form.email.data

		db.session.add(user)

		db.session.commit()

		flash('Details Edited Successfully', 'message')


	return render_template('edit_profile.html', form=form, user=user)

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

	current_time = datetime.datetime.now()

	audio_file_path = "/static/audioFiles/" + current_user.email + '_' + str(current_time) + '.wav'

	wemp_to_wav_convertor("app/static/audioFiles/audio.wav", "app{}".format(audio_file_path))
	
	# Instantiates a client
	client = speech.SpeechClient()

	with open("app{}".format(audio_file_path), "rb") as file:
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

	print(response)

	transcript = ""

	transcript_array = []

	for result in response.results:
		print("Transcript: {}".format(result.alternatives[0].transcript))
		transcript_array.append(result.alternatives[0].transcript)
		transcript+=result.alternatives[0].transcript

	print(transcript)

	audio_obj = Audio(audio_file_name=audio_file_path, transcript=transcript, user_id=current_user.id)

	db.session.add(audio_obj)

	db.session.commit()

	return jsonify({"status":"success", "Transcript":transcript_array})

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

def wemp_to_wav_convertor(input_file, output_file):

	stream = ffmpeg.input(input_file)
	stream = ffmpeg.output(stream, output_file)
	ffmpeg.run(stream)