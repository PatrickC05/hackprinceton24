from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from main.models import User, Goal, GoalDay, Journal
import datetime


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        goalstoday = GoalDay.objects.filter(date=datetime.date.today(), goal__user=request.user)
        count = goalstoday.count()
        goalscompleted = goalstoday.filter(completed=True).count()
        return render(request, 'index.html', {'goalstoday': goalstoday, 'count': count, 'goalscompleted': goalscompleted})
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
    return render(request, 'goals.html')

def therapy(request):
    return render(request, 'therapy.html')

def new_goal(request):
    return render(request, 'new_goal.html')

def profile(request):
    return render(request, 'profile.html')