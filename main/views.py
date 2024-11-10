from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from main.models import User, Goal, GoalDay, Journal, Therapy
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse
import datetime
from main.util import speechtotext, api
import requests
import os
import base64
from dotenv import load_dotenv


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        goalstoday = GoalDay.objects.filter(date=datetime.date.today(), goal__user=request.user).order_by('completed')
        count = goalstoday.count()
        goalscompleted = goalstoday.filter(completed=True).count()
        lasttherapy = Therapy.objects.filter(user=request.user).order_by('-date').first()
        journal = Journal.objects.filter(user=request.user).filter(date__lt=datetime.date.today()).order_by('-date')
        return render(request, 'index.html', {'goalstoday': goalstoday, 'count': count, 'goalscompleted': goalscompleted, 'lasttherapy': lasttherapy, 'journal': journal})
    return render(request, 'index.html')

def signup(request):
    return render(request, 'signup.html')



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', {'error': 'Invalid password'})
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

def signup(request):
    if request.method == 'POST':
        user = User.objects.create_user(username=request.POST['username'], password=request.POST['password'])
        if request.POST.get('phone'):
            user.phone = request.POST['phone']
        user.email = request.POST['email']
        user.first_name = request.POST['first-name']
        user.last_name = request.POST['last-name']
        user.save()
        login(request, user)
        return redirect('index')
    
    return render(request, 'signup.html')

def goals(request):
    if request.method == 'POST':
        frequency = request.POST.get('frequency', "daily")
        frequencyDict = {"daily": "1", "weekly": "2", "monthly": "3"}
        ty = frequencyDict[frequency]
        today = datetime.date.today()
        goal = Goal.objects.create(user=request.user, name=request.POST['goal'], start_date=today, end_date=request.POST['date'], type=ty)
        day = datetime.date.today()
        endday = datetime.datetime.strptime(request.POST['date'], "%Y-%m-%d").date()
        while day <= endday:
            GoalDay.objects.create(goal=goal, date=day)
            day += datetime.timedelta(days=1)
        return redirect('goals')
    usergoals = Goal.objects.filter(user=request.user).filter(end_date__gte=datetime.date.today())
    for goal in usergoals:
        goal.days = GoalDay.objects.filter(goal=goal, date__lte=datetime.date.today()).count()
        goal.completed = GoalDay.objects.filter(goal=goal, date__lte=datetime.date.today(), completed=True).count()
        goal.next = GoalDay.objects.filter(goal=goal, date__gte=datetime.date.today()).order_by('date').first()
    return render(request, 'goals.html', {'goals': usergoals})

def updategoal(request):
    if request.method == 'POST':
        goal = GoalDay.objects.get(id=request.POST['goal_id'])
        goal.completed = not goal.completed
        goal.save()
        return HttpResponse('Success')
    return HttpResponseNotFound()

def therapy(request):
    today = datetime.date.today()
    if request.method == 'POST':
        request.user.therapyscale = request.POST['scale']
        request.user.malevoice = request.POST.get('voice', False) == '1'
        request.user.save()
        return HttpResponse('Success')
    return render(request, 'therapy.html', {'today': today})

def new_goal(request):
    return render(request, 'new_goal.html')

def profile(request):
    return render(request, 'profile.html')

def journal(request):
    today = datetime.date.today()
    journal = Journal.objects.filter(user=request.user)
    todayjournal = journal.filter(date=today).first()
    if request.method == 'POST':
        if todayjournal:
            todayjournal.entry = request.POST['journal_entry']
            todayjournal.save()
        else:
            Journal.objects.create(user=request.user, date=today, entry=request.POST['journal_entry'])
        return redirect('journal')
    journal = journal.filter(date__lt=today).order_by('-date')
    return render(request, 'journal.html', {'today': today, 'journal': journal, 'todayjournal': todayjournal})

def respond(request):
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    if request.method == 'POST':
        audio = request.FILES.get('audio')
        if audio:
            with open('temp.wav', 'wb') as f:
                for chunk in audio.chunks():
                    f.write(chunk)
            speechtotext.convert_audio('temp.wav', 'temp_converted.wav')

            transcription = speechtotext.transcribe_audio('temp_converted.wav')
            os.remove('temp.wav')
            os.remove('temp_converted.wav')

        else:
            transcription = request.POST.get('user_input', '')
            
            if not transcription:
                return JsonResponse({'text': 'No input provided', 'response': ''})

        # Generate the assistant's response
        api.initialize_session(request.user)
        assistant_response = api.generate_assistant_response(request.user, transcription)

        audio_base64 = ""

        if audio:
            # Google Cloud Text-to-Speech API endpoint with API key
            url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_API_KEY}"
            if request.user.malevoice:
                voice = "en-US-Journey-D"
            else:
                voice = "en-US-Journey-O"
            
            # Set up the payload for the Text-to-Speech API
            payload = {
                "input": {"text": assistant_response},
                "voice": {
                    "languageCode": "en-US",
                    "name": voice
                },
                "audioConfig": {"audioEncoding": "MP3"}
            }
            
            # Perform the Text-to-Speech request
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=payload, headers=headers)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Extract audio content and encode to base64
                audio_content = response.json().get("audioContent")
                if audio_content:
                    audio_base64 = audio_content  # This is already base64 encoded from the API
            else:
                print("Error with Text-to-Speech API:", response.json())

        # Return both the transcription and the assistant's response
        return JsonResponse({'text': transcription, 'response': assistant_response, 'audio': audio_base64})

    return HttpResponseNotFound()
