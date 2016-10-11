import datetime
import pytz
import re

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .models import UserProfile, MyCalendar, Event, Guest, EventCustomSettings
from .forms import (RegisterForm, EventForm, AttendingStatusForm, ProfileForm,
    CalendarForm, GuestForm)
from .additional_functions import (COLORS, fill_month, fill_week,
    get_events_from_days, get_number_and_name_of_timezone)


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

def month(request, year, month, day):
    context = {}
    try:
        date_ = datetime.date(int(year), int(month), int(day))
    except ValueError:
        date_ = datetime.datetime.now().date()
        context['date_errors'] = "You enetered wrong date."
    days = fill_month(date_)
    if request.user.is_authenticated():
        profile = get_object_or_404(UserProfile, user=request.user)
        events = profile.get_all_events()
        timezone = pytz.timezone(profile.get_timezone_display())
        context['days'] = get_events_from_days(days, events, timezone, profile)
        context['calendars'] = (profile.get_own_calendars()
            | profile.get_calendars_to_modify()
            | profile.get_calendars_to_read()).distinct()
    else:
        context['days'] = days
    context['choosen_date'] = date_
    return render(request, 'my_calendar/month.html', context)

def week(request, year, month, day):
    context = {}
    try:
        date_ = datetime.date(int(year), int(month), int(day))
    except ValueError:
        date_ = datetime.datetime.now().date()
        context['date_errors'] = "You enetered wrong date."
    days = fill_week(date_)
    if request.user.is_authenticated():
        profile = get_object_or_404(UserProfile, user=request.user)
        events = profile.get_all_events()
        timezone = pytz.timezone(profile.get_timezone_display())
        context['days'] = get_events_from_days(days, events, timezone, profile)
        context['calendars'] = (profile.get_own_calendars()
            | profile.get_calendars_to_modify()
            | profile.get_calendars_to_read()).distinct()
    else:
        context['days'] = days
    context['choosen_date'] = date_
    context['range'] = range(24)
    return render(request, 'my_calendar/week.html', context)

def day(request, year, month, day):
    context = {}
    try:
        date_ = datetime.date(int(year), int(month), int(day))
    except ValueError:
        date_ = datetime.datetime.now().date()
        context['date_errors'] = "You enetered wrong date."
    context['choosen_date'] = date_
    if request.user.is_authenticated():
        profile = get_object_or_404(UserProfile, user=request.user)
        events = profile.get_all_events()
        timezone = pytz.timezone(profile.get_timezone_display())
        context['days'] = get_events_from_days([date_], events,
            timezone, profile)
        # distinct() removes duplicates
        context['calendars'] = (profile.get_own_calendars()
            | profile.get_calendars_to_modify()
            | profile.get_calendars_to_read()).distinct()
    context['range'] = range(24)
    return render(request, 'my_calendar/day.html', context)

def new_calendar(request):
    context = {}
    if request.user.is_authenticated():
        context['colors'] = COLORS
        calendar_form = CalendarForm(data=request.POST or None)
        if request.method == "POST":
            pattern = re.compile("^#[A-Fa-f0-9]{6}$")
            if not request.POST['name']:
                context['errors'] = "Name of calendar is required."
            elif not pattern.match(request.POST['color']):
                context['errors'] = ("Color has to be hexadecimal with hash "
                    + "at the beginning.")
            elif calendar_form.is_valid():
                owner = UserProfile.objects.get(user=request.user)
                name = request.POST['name']
                color = request.POST['color']
                can_read_ids = request.POST.getlist('can_read')
                can_read = UserProfile.objects.filter(id__in=can_read_ids)
                can_modify_ids = request.POST.getlist('can_modify')
                can_modify = UserProfile.objects.filter(id__in=can_modify_ids)
                calendar_ = MyCalendar.objects.create(owner=owner, name=name,
                    color=color)
                calendar_.can_read.add(*can_read)
                calendar_.can_modify.add(*can_modify)
                return redirect('my_calendar:calendar_view',
                    cal_pk=calendar_.pk)
        context['calendar_form'] = calendar_form
    return render(request, 'my_calendar/new_calendar.html', context)

def calendar_view(request, cal_pk):
    context = {}
    if request.user.is_authenticated():
        calendar_ = get_object_or_404(MyCalendar, pk=cal_pk)
        profile = get_object_or_404(UserProfile, user=request.user)
        context['profile'] = profile
        if (profile == calendar_.owner
            or profile in calendar_.can_read.all()
            or profile in calendar_.can_modify.all()):
            if profile == calendar_.owner:
                context['colors'] = COLORS
                calendar_form = CalendarForm(data=request.POST or None,
                    instance=calendar_)
                if request.method == "POST":
                    pattern = re.compile("^#[A-Fa-f0-9]{6}$")
                    if not request.POST['name']:
                        context['errors'] = "Name of calendar is required."
                    elif not pattern.match(request.POST['color']):
                        context['errors'] = ("Color has to be hexadecimal with "
                            + "hash at the beginning.")
                    else:
                        calendar_.name = request.POST['name']
                        calendar_.color = request.POST['color']
                        can_read_ids = request.POST.getlist('can_read')
                        can_read = UserProfile.objects.filter(
                            id__in=can_read_ids)
                        calendar_.can_read.add(*can_read)
                        can_modify_ids = request.POST.getlist('can_modify')
                        can_modify = UserProfile.objects.filter(
                            id__in=can_modify_ids)
                        calendar_.can_modify.add(*can_modify)
                        calendar_.save()
                context['calendar_form'] = calendar_form
            context['calendar'] = calendar_
            events = Event.objects.filter(calendar=calendar_)
            context['events'] = events
        else:
            context['access_denied'] = "You don't have access to this calendar."
    return render(request, 'my_calendar/calendar.html', context)

def new_event(request, cal_pk):
    context = {}
    if request.user.is_authenticated():
        calendar_ = get_object_or_404(MyCalendar, pk=cal_pk)
        profile = get_object_or_404(UserProfile, user=request.user)
        if calendar_.owner == profile:
            settings = EventCustomSettings()
            settings.start = pytz.utc.localize(datetime.datetime.utcnow())
            settings.end = settings.start + datetime.timedelta(minutes=30)
            guest = Guest()
            profile = get_object_or_404(UserProfile, user=request.user)
            timezone = get_number_and_name_of_timezone(profile)
            event_form = EventForm(data=request.POST or None, instance=settings,
                timezone=timezone)
            attending_status_form = AttendingStatusForm(data=request.POST or None, instance=guest)
            if request.method == "POST":
                if event_form.is_valid() and attending_status_form.is_valid():
                    event = Event.objects.create(calendar=calendar_)
                    guest = attending_status_form.save(commit=False)
                    guest.event = event
                    guest.user = calendar_.owner
                    guest.save()
                    event_custom_settings = event_form.save(commit=False)
                    event_custom_settings.guest = guest
                    event_custom_settings.save()
                    return redirect('my_calendar:event_view', event_pk=event.pk)
            context['event_form'] = event_form
            context['attending_status_form'] = attending_status_form
        else:
            context['access_denied'] = ("You don't have access to add "
                + "events to this calendar.")
    return render(request, 'my_calendar/new_event.html', context)

def event_view(request, event_pk=None):
    context = {}
    if not request.user.is_authenticated():
        return render(request, 'my_calendar/event.html', context)
    event = get_object_or_404(Event, pk=event_pk)
    profile = get_object_or_404(UserProfile, user=request.user)
    context['profile'] = profile
    try:
        guest = Guest.objects.get(event=event, user=profile)
        context['user_is_guest'] = True
        context['attending_status_form'] = AttendingStatusForm(instance=guest)
    except Guest.DoesNotExist:
        guest = None
    if (profile == event.calendar.owner
        or profile in event.calendar.can_modify.all()):
        
        event_settings = event.get_owner_settings()
        timezone = get_number_and_name_of_timezone(event_settings)
        context['event_form'] = EventForm(instance=event_settings, timezone=timezone)
        context['guest_form'] = GuestForm(event=event)
        context['event'] = event_settings
        context['guests'] = Guest.objects.filter(event=event)
        
        if request.method == "POST":
            form = None
            
            if 'save_event' in request.POST:
                form = EventForm(data=request.POST, instance=event_settings)
                form_name = 'event_form'
            elif 'save_guest' in request.POST:
                form = GuestForm(data=request.POST, event=event)
                form_name = 'guest_form'
            elif 'save_attending_status' in request.POST and guest != None:
                form = AttendingStatusForm(data=request.POST, instance=guest)
                form_name = 'attending_status_form'

            if form != None and form.is_valid():
                form.save()
                return redirect('my_calendar:event_view', event_pk=event.pk)
            elif form != None:
                context[form_name] = form

    elif guest != None:
        event_settings, settings_belong_to_owner = guest.get_settings()
        timezone = get_number_and_name_of_timezone(event_settings)
        context['event'] = event_settings
        context['guests'] = Guest.objects.filter(event=event)
        context['guest_message'] = ("If you change default settings, you "
            + "won't be able to see changes made by owner of this event.")
        event_form = EventForm(instance=event_settings, timezone=timezone)
        if request.method == "POST" and 'save_attending_status' in request.POST:
            attending_status_form = AttendingStatusForm(data=request.POST, instance=guest)
            if attending_status_form.is_valid():
                attending_status_form.save()
                return redirect('my_calendar:event_view', event_pk=event.pk)
            else:
                context['attending_status_form'] = attending_status_form
        elif request.method == "POST" and 'save_event' in request.POST:
            event_form = EventForm(data=request.POST, instance=event_settings)
            if event_form.is_valid():
                if settings_belong_to_owner:
                    event_form = EventForm(data=request.POST)
                    event_custom_settings = event_form.save(commit=False)
                    event_custom_settings.guest = guest
                    event_custom_settings.save()
                else:
                    event_form.save()
                return redirect('my_calendar:event_view',
                    event_pk=event.pk)
        context['event_form'] = event_form
    elif profile in event.calendar.can_read.all():
        if request.method == "POST":
            context['access_denied'] = ("You don't have access to "
                    + "edit this event.")
        context['event'] = event.get_owner_settings()
        context['guests'] = Guest.objects.filter(event=event)
    else:
        context['access_denied'] = "You don't have access to this event."
    return render(request, 'my_calendar/event.html', context)
