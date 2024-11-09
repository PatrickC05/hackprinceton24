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
    # Record and save raw audio
    # audio = record_until_silence()
    # raw_audio_path = "output_audio_raw.wav"
    # wav.write(raw_audio_path, samplerate, audio)
    # print("Raw audio saved.")

    # Convert raw audio to Whisper-compatible format
    # converted_audio_path = "output_audio_converted.wav"
    # convert_audio(audio_file, converted_audio_path)

    transcribed_text = transcribe_audio(audio_file)
    print(f"Transcribed Text: {transcribed_text}")

    return transcribed_text






# Generate GPT response
# def get_gpt_response(conversation_history):
#     print("Generating GPT response...")
#     try:
#         # Format conversation history for Chat API
#         messages = [{"role": "user", "content": msg.split(": ")[1]} if "User" in msg else {"role": "assistant", "content": msg.split(": ")[1]} for msg in conversation_history]
#         messages.insert(0, {"role": "system", "content": "You are a helpful assistant."})

#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=messages,
#             max_tokens=100,
#             temperature=0.7
#         )
#         print("GPT response generated.")
#         return response.choices[0].message['content']
#     except Exception as e:
#         print(f"Error generating GPT response: {e}")
#         return "I'm sorry, but I couldn't process that request right now."

# # Initialize conversation
# conversation_history = ["User: Hello!"]

# # Main loop
# while True:
#     if transcribed_text.lower() in ["exit", "quit", "stop"]:
#         print("Conversation ended.")
#         break

#     if transcribed_text and f"User: {transcribed_text}" not in conversation_history:
#         conversation_history.append(f"User: {transcribed_text}")
#     else:
#         print("No valid new input detected; awaiting further input.")
#         continue

#     gpt_response = get_gpt_response(conversation_history)
#     print(f"GPT Response: {gpt_response}")

#     client = Client(user_id=PLAY_HT_USER_ID, api_key=PLAY_HT_API_KEY)
#     options = TTSOptions(voice="en_us_male")

#     def generate_speech(gpt_response, client, options):
#         try:
#             response_audio = b""
#             for chunk in client.tts(gpt_response, options):
#                 response_audio += chunk
#             return response_audio
#         except Exception as e:
#             print(f"Error generating speech: {e}")
#             return None

#     response_audio = generate_speech(gpt_response, client, options)
#     if response_audio is not None:
#         audio_data = np.frombuffer(response_audio, dtype=np.int16).astype(np.int16)
#         sd.play(audio_data, samplerate)
#         sd.wait()
#         print("Playback completed.")
#     else:
#         print("No audio generated; skipping playback.")

#     print("\nSay something new...")
#     audio = record_until_silence()
#     wav.write(raw_audio_path, samplerate, audio)

#     convert_audio(raw_audio_path, converted_audio_path)
#     transcribed_text = transcribe_audio(converted_audio_path)
#     print(f"Transcribed Text: {transcribed_text}")