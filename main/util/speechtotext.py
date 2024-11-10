import openai
from dotenv import load_dotenv
import os
import sounddevice as sd
import numpy as np
import whisper
import pyht
from pyht import Client
import scipy.io.wavfile as wav
from pyht.client import TTSOptions
import ffmpeg
import warnings

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
PLAY_HT_USER_ID = os.getenv("PLAY_HT_USER_ID")
PLAY_HT_API_KEY = os.getenv("PLAY_HT_API_KEY")

samplerate = 44100  # samples per second
threshold = 0.1  # sensitivity to silence
chunk_size = samplerate  # Full second chunks for silence detection

# Load Whisper model
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=FutureWarning)
    model = whisper.load_model("base")


# Silence detection
def is_silent(data, threshold):
    silence_detected = np.max(np.abs(data)) < threshold
    print(f"Silence detected: {silence_detected}")
    return silence_detected


# Record until silence is detected
def record_until_silence():
    print("Recording...")
    with sd.InputStream(samplerate=samplerate, channels=1) as stream:
        audio_data = []
        silence_counter = 0
        while True:
            chunk, overflowed = stream.read(chunk_size)
            if not overflowed:
                audio_data.append(chunk)
            if is_silent(chunk, threshold):
                silence_counter += 1
                if silence_counter > 3:
                    print("Silence detected. Stopping recording.")
                    break
            else:
                silence_counter = 0

    audio_data = np.concatenate(audio_data, axis=0)
    print("Recording completed.")
    return audio_data


# Function to convert audio to Whisper-compatible format using FFmpeg
def convert_audio(input_path, output_path):
    print("Converting audio to Whisper-compatible format...")
    try:
        ffmpeg.input(input_path).output(output_path, format='wav', acodec='pcm_s16le', ac=1, ar='16000').run()
        print("Conversion completed.")
    except ffmpeg.Error as e:
        print(f"Error during audio conversion: {e.stderr.decode()}")


# Transcribe converted audio
def transcribe_audio(audio_path):
    print("Transcribing audio...")
    result = model.transcribe(audio_path)
    print("Transcription complete.")
    return result['text']



def main(audio_file):
    transcribed_text = transcribe_audio(audio_file)
    print(f"Transcribed Text: {transcribed_text}")

    return transcribed_text
