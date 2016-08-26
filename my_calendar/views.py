from pytz import common_timezones_set

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from .forms import RegisterForm, LoginForm
from .models import UserProfile


def index(request):
    return render(request, "my_calendar/index.html")
    
    
def register(request):
    context = {}
    if request.method == "POST":
        register_form = RegisterForm(data=request.POST)
        if register_form.is_valid():
            user = register_form.save()
            unhashed_password = user.password
            user.set_password(user.password)
            user.save()
            profile = UserProfile.objects.create(user=user)
            profile.timezone = request.POST['timezone']
            profile.save()
            user_obj = authenticate(username=user.username, password=unhashed_password)
            login(request, user_obj)
            return redirect('my_calendar:index')
        else:
            print(register_form.errors)
    else:
        register_form = RegisterForm()
    context['register_form'] = register_form
    timezones = list(common_timezones_set)
    timezones.sort()
    context['timezones'] = timezones
    return render(request, "my_calendar/register.html", context)
