import datetime
import pytz
import re

from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib.postgres.search import SearchVector
from django.contrib.auth.models import User

from .models import UserProfile, MyCalendar, Event, Guest
from .forms import (RegisterForm, EventForm, AttendingStatusForm, ProfileForm,
    CalendarForm, GuestForm)
from .additional_functions import (COLORS, fill_month, fill_week,
    get_events_from_days, get_number_and_name_of_timezone)


class AuthRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        allowed_urls = [
            reverse('my_calendar:index'),
            reverse('my_calendar:user_login'),
            reverse('my_calendar:register'),
        ]
        if (request.path.startswith('/admin')
                or request.path in allowed_urls
                or request.user.is_authenticated()):
            return None
        return redirect('my_calendar:index')


def index(request):
    if request.user.is_authenticated():
        return redirect('my_calendar:profile', username=request.user.username)
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
    context['other_calendars'] = (profile.get_calendars_to_read()
        | profile.get_calendars_to_modify()).exclude(owner=profile).distinct()
    context['upcoming_events'] = profile.get_upcoming_events(5)

    return render(request, 'my_calendar/profile.html', context)

def user_login(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('my_calendar:profile', username=username)
        else:
            context['login_errors'] = "Wrong username or password."
    return render(request, 'my_calendar/index.html', context)

def user_logout(request):
    logout(request)
    return redirect('my_calendar:index')

def month(request, year, month, day):
    context = {}
    if request.user.is_authenticated():
        try:
            date_ = datetime.date(int(year), int(month), int(day))
        except ValueError:
            date_ = datetime.datetime.now().date()
            context['date_errors'] = "You enetered wrong date."
        days = fill_month(date_)
        profile = get_object_or_404(UserProfile, user=request.user)
        events = profile.get_all_events()
        timezone = pytz.timezone(profile.get_timezone_display())
        context['days'] = get_events_from_days(days, events, timezone, profile)
        context['calendars'] = (profile.get_calendars_to_modify()
            | profile.get_calendars_to_read()).distinct()
        context['chosen_date'] = date_
        chosen_month = date_.month
        decreasing_date = date_
        while decreasing_date.month == chosen_month:
            decreasing_date -= datetime.timedelta(days=1)
        decreasing_date = decreasing_date.replace(day=1)
        context['earlier'] = decreasing_date
        increasing_date = date_
        while increasing_date.month == chosen_month:
            increasing_date += datetime.timedelta(days=1)
        increasing_date = increasing_date.replace(day=1)
        context['later'] = increasing_date
    return render(request, 'my_calendar/month.html', context)

def week(request, year, month, day):
    context = {}
    if request.user.is_authenticated():
        try:
            date_ = datetime.date(int(year), int(month), int(day))
        except ValueError:
            date_ = datetime.datetime.now().date()
            context['date_errors'] = "You enetered wrong date."
        days = fill_week(date_)
        profile = get_object_or_404(UserProfile, user=request.user)
        events = profile.get_all_events()
        timezone = pytz.timezone(profile.get_timezone_display())
        context['days'] = get_events_from_days(days, events, timezone, profile)
        context['calendars'] = (profile.get_calendars_to_modify()
            | profile.get_calendars_to_read()).distinct()
        context['chosen_date'] = date_
        context['earlier'] = date_ - datetime.timedelta(days=7)
        context['later'] = date_ + datetime.timedelta(days=7)
        context['range'] = range(24)
        context['Monday'] = date_ - datetime.timedelta(days=date_.weekday())
        context['Sunday'] = context['Monday'] + datetime.timedelta(days=6)
    return render(request, 'my_calendar/week.html', context)

def day(request, year, month, day):
    context = {}
    if request.user.is_authenticated():
        try:
            date_ = datetime.date(int(year), int(month), int(day))
        except ValueError:
            date_ = datetime.datetime.now().date()
            context['date_errors'] = "You enetered wrong date."
        context['chosen_date'] = date_
        context['earlier'] = date_ - datetime.timedelta(days=1)
        context['later'] = date_ + datetime.timedelta(days=1)

        profile = get_object_or_404(UserProfile, user=request.user)
        events = profile.get_all_events()
        timezone = pytz.timezone(profile.get_timezone_display())
        context['days'] = get_events_from_days([date_], events,
            timezone, profile)
        context['calendars'] = (profile.get_calendars_to_modify()
            | profile.get_calendars_to_read()).distinct()
        context['range'] = range(24)
    return render(request, 'my_calendar/day.html', context)

def new_calendar(request):
    context = {}
    if request.user.is_authenticated():
        context['colors'] = COLORS
        owner = UserProfile.objects.get(user=request.user)
        calendar_form = CalendarForm(data=request.POST or None, owner=owner)
        if request.method == "POST":
            pattern = re.compile("^#[A-Fa-f0-9]{6}$")
            if not request.POST['name']:
                context['form_errors'] = "Name of calendar is required."
            elif not pattern.match(request.POST['color']):
                context['form_errors'] = ("Color has to be hexadecimal with hash "
                    + "at the beginning.")
            elif calendar_form.is_valid():
                name = request.POST['name']
                color = request.POST['color']
                readers_ids = request.POST.getlist('readers')
                new_readers = UserProfile.objects.filter(id__in=readers_ids)
                modifiers_ids = request.POST.getlist('modifiers')
                new_modifiers = UserProfile.objects.filter(id__in=modifiers_ids)
                calendar_ = MyCalendar.objects.create(owner=owner, name=name,
                    color=color)
                calendar_.readers.add(*new_readers)
                calendar_.modifiers.add(*new_modifiers)
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
        if (profile in calendar_.readers.all()
            or profile in calendar_.modifiers.all()):
            if profile == calendar_.owner:
                context['colors'] = COLORS
                calendar_form = CalendarForm(data=request.POST or None,
                    instance=calendar_, owner=profile)
                if request.method == "POST":
                    pattern = re.compile("^#[A-Fa-f0-9]{6}$")
                    if not request.POST['name']:
                        context['form_errors'] = "Name of calendar is required."
                    elif not pattern.match(request.POST['color']):
                        context['form_errors'] = ("Color has to be hexadecimal with "
                            + "hash at the beginning.")
                    else:
                        calendar_.name = request.POST['name']
                        calendar_.color = request.POST['color']
                        readers_ids = request.POST.getlist('readers')
                        updated_readers = UserProfile.objects.filter(
                            id__in=readers_ids)
                        calendar_.readers.add(*updated_readers)
                        modifiers_ids = request.POST.getlist('modifiers')
                        updated_modifiers = UserProfile.objects.filter(
                            id__in=modifiers_ids)
                        calendar_.modifiers.add(*updated_modifiers)
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
            event = Event()
            event.start = pytz.utc.localize(datetime.datetime.utcnow())
            event.end = event.start + datetime.timedelta(minutes=30)
            timezone = get_number_and_name_of_timezone(profile)
            event_form = EventForm(data=request.POST or None, instance=event,
                timezone=timezone)
            attending_status_form = AttendingStatusForm(data=request.POST or None)
            if request.method == "POST":
                if event_form.is_valid() and attending_status_form.is_valid():
                    event = event_form.save(commit=False)
                    event.calendar = calendar_
                    event.save()
                    guest = attending_status_form.save(commit=False)
                    guest.event = event
                    guest.user = calendar_.owner
                    guest.save()
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
    if (profile in event.calendar.modifiers.all()):

        timezone = get_number_and_name_of_timezone(event)
        context['event_form'] = EventForm(instance=event, timezone=timezone)
        context['guest_form'] = GuestForm(event=event)
        context['event'] = event
        context['guests'] = Guest.objects.filter(event=event)

        if request.method == "POST":
            form = None

            if 'save_event' in request.POST:
                form = EventForm(data=request.POST, instance=event)
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
        context['event'] = event
        context['guests'] = Guest.objects.filter(event=event)
        if request.method == "POST":
            if 'save_attending_status' in request.POST:
                form = AttendingStatusForm(data=request.POST, instance=guest)
                if form.is_valid():
                    form.save()
                    return redirect('my_calendar:event_view', event_pk=event.pk)
                else:
                    context['attending_status_form'] = form
            else:
                context['access_denied'] = ("You don't have access to "
                        + "edit this event.")
    elif profile in event.calendar.readers.all():
        if request.method == "POST":
            context['access_denied'] = ("You don't have access to "
                    + "edit this event.")
        context['event'] = event
        context['guests'] = Guest.objects.filter(event=event)

    else:
        context['access_denied'] = "You don't have access to this event."
    return render(request, 'my_calendar/event.html', context)

def search(request):
    phrase = request.GET.get('phrase')
    context = {'phrase': phrase}
    context['users'] = (UserProfile.objects.filter(
        user__first_name__startswith=phrase) |
        UserProfile.objects.filter(
        user__last_name__startswith=phrase)).distinct()
    context['calendars'] = MyCalendar.objects.filter(
        name__contains=phrase)
    context['events'] = Event.objects.filter(
        title__contains=phrase)
    return render(request, 'my_calendar/search.html', context)
