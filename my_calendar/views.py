from calendar import monthrange
import datetime
import pytz
import re

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .models import UserProfile, MyCalendar, Event, Guest, EventCustomSettings
from .forms import RegisterForm, EventForm, StateForm, ProfileForm


def index(request):
    return render(request, "my_calendar/index.html")
    
def register(request):
    context = {}
    if request.method == "POST":
        register_form = RegisterForm(data=request.POST)
        profile_form = ProfileForm(data=request.POST)
        if register_form.is_valid() and profile_form.is_valid():
            user = register_form.save()
            unhashed_password = user.password
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            user_obj = authenticate(username=user.username,
                password=unhashed_password)
            login(request, user_obj)
            return redirect('my_calendar:profile', username=user.username)
        else:
            print(register_form.errors)
    else:
        register_form = RegisterForm()
        profile_form = ProfileForm()
    context['register_form'] = register_form
    context['profile_form'] = profile_form
    return render(request, "my_calendar/register.html", context)

def profile(request, username):
    context = {}
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=user)
    context['profile'] = profile
    calendars = profile.get_own_calendars()
    context['calendars'] = calendars
    return render(request, 'my_calendar/profile.html', context)
    
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
    

def calendar_view(request, cal_pk=None):
    context = {}
    context['colors'] = COLORS
    if request.method == "POST":
        pattern = re.compile("^#[A-Fa-f0-9]{6}$")
        if not request.user.is_authenticated:
            context['errors'] = "Only users can create and edit a calendar."
        elif not request.POST['name']:
            context['errors'] = "Name of calendar is required."
        elif not pattern.match(request.POST['color']):
            context['errors'] = ("Color has to be hexadecimal with hash "
                + "at the beginning.")
        else:
            # editing
            if cal_pk != None:
                calendar_ = MyCalendar.objects.get(pk=cal_pk)
                calendar_.name = request.POST['name']
                calendar_.color = request.POST['color']
                calendar_.save()
            # creating new calendar
            else:
                owner = UserProfile.objects.get(user=request.user)
                name = request.POST['name']
                color = request.POST['color']
                calendar_ = MyCalendar.objects.create(owner=owner, name=name,
                    color=color)
            context['calendar'] = calendar_
            # redirect to make url look better
            # e.g. if I make a new calendar,
            # browser will redirect to 'calendar/1'
            # and not 'calendar/new' which is a page for making new calendars
            return redirect('my_calendar:calendar_view', cal_pk=calendar_.pk)
    if cal_pk != None:
        calendar_ = get_object_or_404(MyCalendar, pk=cal_pk)
        context['calendar'] = calendar_
        events = Event.objects.filter(calendar=calendar_)
        context['events'] = events
        return render(request, 'my_calendar/calendar.html', context)
    return render(request, 'my_calendar/new_calendar.html', context)
    
COLORS = (
    "E81AD4",
    "8F00FF",
    "6214CC",
    "464AFF",
)

def event_view(request, cal_pk=None, event_pk=None):
    context = {}
    if event_pk != None:
        event = get_object_or_404(Event, pk=event_pk)
        settings = event.get_owner_settings()
        guest = settings.guest
        timezone = {
            'tz': pytz.timezone(settings.get_timezone_display()),
            'number': settings.timezone,
        }
    else:
        settings = EventCustomSettings()
        settings.start = pytz.utc.localize(datetime.datetime.utcnow())
        settings.end = settings.start + datetime.timedelta(minutes=30)
        guest = Guest()
        if request.user.is_authenticated():
            profile = get_object_or_404(UserProfile, user=request.user)
            timezone = {
                'tz': pytz.timezone(profile.get_timezone_display()),
                'number': profile.timezone,
            }
        else:
            timezone = {
                'tz': pytz.utc,
                'number': 436,
            }
    event_form = EventForm(data=request.POST or None, instance=settings,
        start=settings.start, end=settings.end, timezone=timezone)
    state_form = StateForm(data=request.POST or None, instance=guest)
    if request.method == "POST":
        if event_form.is_valid() and state_form.is_valid():
            if event_pk != None:
                state_form.save()
                event_form.save()
            else:
                calendar_ = get_object_or_404(MyCalendar, pk=cal_pk)
                event = Event.objects.create(calendar=calendar_)
                guest = state_form.save(commit=False)
                guest.event = event
                guest.user = calendar_.owner
                # what if creator of event is not calendar.owner?
                guest.save()
                event_custom_settings = event_form.save(commit=False)
                event_custom_settings.guest = guest
                event_custom_settings.save()
            return redirect('my_calendar:event_view', event_pk=event.pk)
    context['event_form'] = event_form
    context['state_form'] = state_form
    if event_pk != None:
        event = get_object_or_404(Event, pk=event_pk)
        context['event'] = event.get_owner_settings()
        guest = Guest.objects.get(user=event.calendar.owner, event=event)
        context['state'] = guest.get_state_display()
        return render(request, 'my_calendar/event.html', context)
    return render(request, 'my_calendar/new_event.html', context)
