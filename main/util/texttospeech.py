from pyht import Client, TTSOptions
from dotenv import load_dotenv
import os
import traceback

# Load environment variables
load_dotenv()

# Set up PlayHT client credentials
PLAY_HT_USER_ID = os.getenv("PLAY_HT_USER_ID")
PLAY_HT_API_KEY = os.getenv("PLAY_HT_API_KEY")

# Initialize the PlayHT client
client = Client(user_id=PLAY_HT_USER_ID, api_key=PLAY_HT_API_KEY)
print("PlayHT client initialized")

# Set up the TTS options with valid voice and format
options = TTSOptions(
    voice="larry",  # Replace with an actual voice ID from Play.ht
    format="wav"    # Use the correct format identifier
)

import time

def text_to_speech(text, output_file="output.wav"):
    try:
        # Generate speech and retrieve audio data from the client
        audio_generator = client.tts(text, options)
        print(f"Received audio data of type {type(audio_generator)}")

        # Set a maximum wait time to prevent infinite loops
        max_wait_time = 60  # in seconds
        start_time = time.time()

        # Open the output file in write-binary mode
        with open(output_file, "wb") as f:
            for idx, chunk in enumerate(audio_generator):
                print(f"Chunk {idx}: Type {type(chunk)}")

                # Check if maximum wait time exceeded
                if time.time() - start_time > max_wait_time:
                    print("Timeout: Audio generation took too long.")
                    break

                # If the chunk is bytes, write it to the file
                if isinstance(chunk, bytes):
                    f.write(chunk)
                else:
                    # Check if chunk is a dict containing an error
                    if isinstance(chunk, dict):
                        print("Error from API:", chunk)
                        return
                    else:
                        print(f"Received unexpected chunk type: {type(chunk)}")
                        continue

        print(f"Audio saved to {output_file}")

    except Exception as e:
        print("Error generating speech:", e)
        import traceback
        traceback.print_exc()

import requests
import time

def text_to_speech_direct(text, output_file="output.wav"):
    try:
        # Set up the request headers
        headers = {
            'Authorization': PLAY_HT_API_KEY,
            'X-User-ID': PLAY_HT_USER_ID,
            'Content-Type': 'application/json'
        }

        # Set up the request payload
        payload = {
            'voice': 'larry',  # Replace with a valid voice ID
            'content': [text],
            'output_format': 'wav'
        }

        # Submit the TTS request
        response = requests.post('https://play.ht/api/v1/convert', json=payload, headers=headers)
        print("Submit TTS Response:", response.json())

        if response.status_code != 200:
            print("Error submitting TTS request:", response.text)
            return

        transcription_id = response.json().get('transcriptionId')
        if not transcription_id:
            print("No transcription ID received.")
            return

        # Poll for the transcription status
        status_url = f'https://play.ht/api/v1/articleStatus?transcriptionId={transcription_id}'

        max_wait_time = 60  # seconds
        poll_interval = 5  # seconds
        start_time = time.time()

        while True:
            if time.time() - start_time > max_wait_time:
                print("Timeout: Audio generation took too long.")
                return

            status_response = requests.get(status_url, headers=headers)
            status_data = status_response.json()
            print("Status Response:", status_data)

            if status_data.get('converted'):
                audio_url = status_data['audioUrl']
                break
            else:
                time.sleep(poll_interval)

        # Download the audio file
        audio_response = requests.get(audio_url)
        with open(output_file, 'wb') as f:
            f.write(audio_response.content)
        print(f"Audio saved to {output_file}")

    except Exception as e:
        print("Error generating speech:", e)
        import traceback
        traceback.print_exc()

# import requests

url = "https://api.play.ht/api/v2/tts/stream"

payload = {
    "voice": "s3://voice-cloning-zero-shot/d9ff78ba-d016-47f6-b0ef-dd630f59414e/female-cs/manifest.json",
    "output_format": "mp3"
}
headers = {
    "accept": "audio/mpeg",
    "content-type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)

# Example usage
text = "Hello, this is a text-to-speech test using Play.ht."
text_to_speech_direct(text, "output.wav")
