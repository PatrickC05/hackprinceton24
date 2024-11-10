import os
import whisper
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import logging
import ffmpeg


def convert_audio(input_path, output_path):
    try:
        ffmpeg.input(input_path).output(output_path, format='wav', acodec='pcm_s16le', ac=1, ar='16000').run()
        logging.info(f"Converted audio file to {output_path}")
    except ffmpeg.Error as e:
        logging.error(f"FFmpeg error: {e.stderr.decode()}")
        raise

# Load the Whisper model
model = whisper.load_model("base")

@csrf_exempt
def transcribe_audio(request):
    if request.method == 'POST' and 'audio' in request.FILES:
        audio_file = request.FILES['audio']
        logging.info(f"Received audio file: {audio_file.name}, Size: {audio_file.size}")

        temp_path = default_storage.save("temp_recording.wav", audio_file)
        logging.info(f"Saved temporary audio file at {temp_path}")

        converted_path = os.path.join(settings.MEDIA_ROOT, "temp_recording_converted.wav")
        convert_audio(temp_path, converted_path)

        try:
            transcription = model.transcribe(converted_path)["text"]
            logging.info(f"Transcription result: {transcription}")

            default_storage.delete(temp_path)
            default_storage.delete(converted_path)

            return JsonResponse({"transcription": transcription})

        except Exception as e:
            logging.error(f"Error during transcription: {e}")
            default_storage.delete(temp_path)
            default_storage.delete(converted_path)
            return JsonResponse({"error": "Unable to transcribe audio."}, status=500)

    logging.warning("Invalid request: No audio file provided or incorrect method.")
    return JsonResponse({"error": "Invalid request"}, status=400)