from pytz import common_timezones_set

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .forms import RegisterForm, LoginForm
from .models import UserProfile


def index(request):
    context = {}
    context['login_form'] = LoginForm()
    return render(request, "my_calendar/index.html", context)
    
    
def register(request):
    context = {}
    if request.method == "POST":
        register_form = RegisterForm(data=request.POST)
        timezone = request.POST.get('timezone', '')
        if not timezone in common_timezones_set:
            context['wrong_timezone'] = "Wrong timezone was chosen."
        elif register_form.is_valid():
            user = register_form.save()
            unhashed_password = user.password
            user.set_password(user.password)
            user.save()
            profile = UserProfile.objects.create(user=user)
            profile.timezone = timezone
            profile.save()
            user_obj = authenticate(username=user.username, password=unhashed_password)
            login(request, user_obj)
            return redirect('my_calendar:profile', username=user.username)
        else:
            print(register_form.errors)
    else:
        register_form = RegisterForm()
    context['register_form'] = register_form
    timezones = list(common_timezones_set)
    timezones.sort()
    context['timezones'] = timezones
    return render(request, "my_calendar/register.html", context)

def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=user)
    return render(request, 'my_calendar/profile.html', {'profile': profile})
    
def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('my_calendar:profile', username=user.username)
        else:
            login_form = LoginForm(request.POST)
    else:
        login_form = LoginForm()
    return render(request, 'my_calendar/index.html', {'login_form': login_form})
    
def user_logout(request):
    logout(request)
    return redirect('my_calendar:index')