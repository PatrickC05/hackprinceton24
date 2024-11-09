import openai
from dotenv import load_dotenv
import os
import sounddevice as sd
import numpy as np
import time
import whisper
import pyht
from pyht import Client
import scipy.io.wavfile as wav
from pyht.client import TTSOptions
import io

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the parameters for the audio stream
samplerate = 44100  # samples per second
threshold = 0.01  # sensitivity to silence

# Function to detect silence
def is_silent(data, threshold):
    return np.max(np.abs(data)) < threshold

# Function to capture audio until silence is detected
def record_until_silence():
    print("Recording...")
    with sd.InputStream(samplerate=samplerate, channels=1) as stream:
        audio_data = []
        while True:
            # Record a chunk of audio
            chunk, overflowed = stream.read(samplerate)
            if not overflowed:
                audio_data.append(chunk)
            # Check if the audio chunk is silent
            if is_silent(chunk, threshold):
                print("Silence detected. Stopping recording.")
                break

    # Convert the list of audio chunks into a numpy array
    audio_data = np.concatenate(audio_data, axis=0)
    return audio_data

# Record audio until silence
audio = record_until_silence()

# Save the recorded audio as a .wav file
audio_path = "output_audio.wav"
wav.write(audio_path, samplerate, audio)

# Load Whisper model
model = whisper.load_model("base")

# Function to transcribe audio
def transcribe_audio(audio_path):
    result = model.transcribe(audio_path)
    return result['text']

# Transcribe the recorded audio
transcribed_text = transcribe_audio(audio_path)

# Print the transcribed text
print(f"Transcribed Text: {transcribed_text}")

# Get GPT response with conversation history
def get_gpt_response(conversation_history):
    # Format the conversation history into a prompt for GPT
    prompt = "\n".join(conversation_history) + "\nUser: " + conversation_history[-1].split(": ")[1] + "\nAI:"
    
    response = openai.Completion.create(
        engine="text-davinci-003",  # or another engine if preferred
        prompt=prompt,
        max_tokens=100,
        temperature=0.7
    )
    return response.choices[0].text.strip()

# Initialize conversation history
conversation_history = ["User: Hello!"]

# Start the conversation loop
while True:
    # Get GPT response based on the transcribed text
    conversation_history.append(f"User: {transcribed_text}")
    gpt_response = get_gpt_response(conversation_history)

    # Print GPT response
    print(f"GPT Response: {gpt_response}")
    
    # Convert GPT response to speech using PlayHT
    PLAY_HT_USER_ID = "maC14RhFlyWgpH4Lq5TYVNbmkqD2"
    PLAY_HT_API_KEY = "0dcdf93e4e144f5c90c9c4d84bf4c863"
    client = Client(user_id=PLAY_HT_USER_ID, api_key=PLAY_HT_API_KEY)
    
    # Define the TTS options (you can customize the voice)
    options = TTSOptions(voice="en_us_male")  # or any other voice of your choice
    
    # Generate the speech for the GPT response
    response_audio = b""
    for chunk in client.tts(gpt_response, options):
        response_audio += chunk
    
    # Play the generated speech audio using sounddevice
    # Convert bytes to numpy array for playback
    audio_data = np.frombuffer(response_audio, dtype=np.int16)
    sd.play(audio_data, samplerate)
    sd.wait()  # Wait until audio is finished playing

    # Record the next user's speech and process it
    print("\nSay something new...")
    audio = record_until_silence()  # Wait for user input

    # Save the next recorded audio
    wav.write(audio_path, samplerate, audio)
    
    # Transcribe the new audio
    transcribed_text = transcribe_audio(audio_path)
    print(f"Transcribed Text: {transcribed_text}")
    
    # Optionally, stop after a set number of turns or allow user to exit the loop
    if transcribed_text.lower() in ["exit", "quit", "stop"]:
        print("Conversation ended.")
        break
