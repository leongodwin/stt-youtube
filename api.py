import os
from flask import Flask, request
from pytube import YouTube
from moviepy.editor import AudioFileClip
import openai

# Function to download a YouTube video
def download_video(url):
    yt = YouTube(url)
    video = yt.streams.first().download()
    return video

# Function to extract audio from the video
def extract_audio(video):
    audio = AudioFileClip(video)
    audio_file = "audio.wav"
    audio.write_audiofile(audio_file)
    return audio_file

# Function to divide the audio into 30-second chunks
def divide_audio(audio):
    audio_clip = AudioFileClip(audio)
    duration = audio_clip.duration
    chunks = []
    for i in range(0, int(duration), 30):
        end = i + 30 if i + 30 < duration else duration
        chunk_file = f"chunk{i}_{end}.wav"
        audio_clip.subclip(i, end).write_audiofile(chunk_file)
        chunks.append(chunk_file)
    return chunks

# Function to transcribe the audio using the OpenAI Whisper API
def transcribe_audio(audio):
    # Open the audio file
    with open(audio, "rb") as audio_file:
        # Transcribe the audio file
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    # Return the transcription
    return transcript["text"]

# Function to clean up the temporary files
def clean_up(files):
    for file in files:
        if os.path.exists(file):
            os.remove(file)

# REST API
app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello_world():
    return "Hello, World!"

@app.route('/transcribe', methods=['POST'])
def transcribe():
    url = request.json['url']
    video = download_video(url)
    audio = extract_audio(video)
    chunks = divide_audio(audio)
    transcription = ''
    for chunk in chunks:
        transcription += transcribe_audio(chunk) + ' '
    clean_up([video, audio] + chunks)
    return transcription

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
