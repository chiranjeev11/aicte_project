from flask import render_template, request, jsonify
from google.cloud import speech
# from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
import os
import os.path
from os import path

from app import app
import ffmpeg
  
  



@app.route('/')
def index():

    return render_template('index.html')

@app.route('/audioBlob', methods=['GET', 'POST'])
def convertSpeechToText():
    data = request.files['audio_file'].read()

    # print(data)


    if path.exists("app/static/audioFiles/audio.wav"):
        os.remove("app/static/audioFiles/audio.wav")

    with open("app/static/audioFiles/audio.wav", "wb") as file:
        file.write(data)

    if path.exists("app/static/audioFiles/audio_converted_ffmpeg.wav"):
        os.remove("app/static/audioFiles/audio_converted_ffmpeg.wav")

    wemp_to_wav_convertor("app/static/audioFiles/audio.wav", "app/static/audioFiles/audio_converted_ffmpeg.wav")
    
    # Instantiates a client
    client = speech.SpeechClient()

    with open("app/static/audioFiles/audio_converted_ffmpeg.wav", "rb") as file:
        content = file.read()



    # delete_blob('aicte', 'audio')
    
    # upload_blob("aicte", "app/static/audioFiles/audio.wav","preamble.wav" )

    # download_blob('aicte', 'audio.wav', 'app/static/downloadAudio/audio1.wav')


    

    # The name of the audio file to transcribe
    # gcs_uri = "gs://aicte/audio.wav"

    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        # sample_rate_hertz=48000,
        # audio_channel_count = 2,
        language_code="en-US",
        # model="video"
    )

    # # Detects speech in the audio file
    operation = client.long_running_recognize(config=config, audio=audio)

    # print(response)audio.wav



    response = operation.result(timeout=90)

    print(response)

    transcript_array = []

    for result in response.results:
        print("Transcript: {}".format(result.alternatives[0].transcript))
        transcript_array.append(result.alternatives[0].transcript)

    print(transcript_array)

    return jsonify({"status":"success", "Transcript":transcript_array})

    


    


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "aicte"
    # The path to your file to upload
    # source_file_name = data
    # The ID of your GCS object
    # destination_blob_name = "audio"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )

    
def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""
    # bucket_name = "your-bucket-name"

    storage_client = storage.Client()

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name)

    for blob in blobs:
        print(blob.name)


def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()

    print("Blob {} deleted.".format(blob_name))


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The ID of your GCS object
    # source_blob_name = "storage-object-name"

    # The path to which the file should be downloaded
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Downloaded storage object {} from bucket {} to local file {}.".format(
            source_blob_name, bucket_name, destination_file_name
        )
    )


def wemp_to_wav_convertor(input_file, output_file):

    stream = ffmpeg.input(input_file)
    stream = ffmpeg.output(stream, output_file)
    ffmpeg.run(stream)