from calendar import monthrange
import datetime
import re

from pytz import common_timezones_set

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .models import UserProfile, MyCalendar
from .forms import RegisterForm

def index(request):
    return render(request, "my_calendar/index.html")
    
    
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
    context = {}
    next_page = request.GET.get("nextpage", "my_calendar:index")
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect(next_page)
        else:
            context['login_errors'] = "Wrong username or password."
    return render(request, 'my_calendar/index.html', context)
    
def user_logout(request):
    logout(request)
    next_page = request.GET.get("nextpage", "my_calendar:index")
    return redirect(next_page)
    
def fill_month(date_):
    '''
    Function that returns list of days of month for given date
    plus the days that fill the month to the full weeks, e.g.:
        -> if first day of month is tuesday,
        the function will also return a last day of the previous month
        -> if last day of month is friday,
        the function will also return two first days of the next month    
    '''
    first = datetime.date(date_.year, date_.month, 1)
    while first.weekday():
        first = first - datetime.timedelta(days=1)
    ## monthrange returns weekday of the first day and number of days in month
    last_day = monthrange(date_.year, date_.month)[1]
    last = datetime.date(date_.year, date_.month, last_day)
    while last.weekday() != 6:
        last = last + datetime.timedelta(days=1)
    days = []
    while first:
        days.append(first)
        if first == last:
            break
        first = first + datetime.timedelta(days=1)
    return days

def month(request, year, month, day):
    context = {}
    try:
        date_ = datetime.date(int(year), int(month), int(day))
    except ValueError:
        date_ = datetime.datetime.now().date()
        context['date-errors'] = "You enetered wrong date."
    days = fill_month(date_)
    context['days'] = days
    context['choosen_date'] = date_
    return render(request, 'my_calendar/month.html', context)
    
def fill_week(date_):
    '''
    Function that returns list of days of week for given date.   
    '''
    first = date_
    while first.weekday():
        first = first - datetime.timedelta(days=1)
    last = date_
    while last.weekday() != 6:
        last = last + datetime.timedelta(days=1)
    days = []
    while first:
        days.append(first)
        if first == last:
            break
        first = first + datetime.timedelta(days=1)
    return days
    
def week(request, year, month, day):
    context = {}
    try:
        date_ = datetime.date(int(year), int(month), int(day))
    except ValueError:
        date_ = datetime.datetime.now().date()
        context['date-errors'] = "You enetered wrong date."
    days = fill_week(date_)
    context['days'] = days
    context['choosen_date'] = date_
    return render(request, 'my_calendar/week.html', context)
    
def day(request, year, month, day):
    context = {}
    try:
        date_ = datetime.date(int(year), int(month), int(day))
    except ValueError:
        date_ = datetime.datetime.now().date()
        context['date-errors'] = "You enetered wrong date."
    context['choosen_date'] = date_
    return render(request, 'my_calendar/day.html', context)
    

def new_calendar(request):
    context = {}
    if request.method == "POST":
        pattern = re.compile("^#[A-Fa-f0-9]{6}$")
        if not request.user.is_authenticated:
            context['errors'] = "Only users can create a calendar."
        elif not request.POST['name']:
            context['errors'] = "Name of calendar is required."
        elif not pattern.match(request.POST['color']):
            context['errors'] = "Color has to be hexadecimal with hash at the beginning."
        else:
            owner = UserProfile.objects.get(user=request.user)
            name = request.POST['name']
            color = request.POST['color']
            calendar_ = MyCalendar.objects.create(owner=owner, name=name, color=color)
            return redirect('my_calendar:calendar_view', cal_pk=calendar_.pk)
    context['colors'] = COLORS
    return render(request, 'my_calendar/new_calendar.html', context)
    
def calendar_view(request, cal_pk):
    context = {}
    calendar_ = MyCalendar.objects.get(pk=cal_pk)
    if request.method == "POST":
        pattern = re.compile("^#[A-Fa-f0-9]{6}$")
        if not request.user.is_authenticated:
            context['errors'] = "Only users can create a calendar."
        elif not request.POST['name']:
            context['errors'] = "Name of calendar is required."
        elif not pattern.match(request.POST['color']):
            context['errors'] = "Color has to be hexadecimal with hash at the beginning."
        else:
            calendar_.name = request.POST['name']
            calendar_.color = request.POST['color']
            calendar_.save()
    context['calendar'] = calendar_
    context['colors'] = COLORS
    return render(request, 'my_calendar/calendar.html', context)
    
COLORS = (
    "E81AD4",
    "8F00FF",
    "6214CC",
    "464AFF",
)