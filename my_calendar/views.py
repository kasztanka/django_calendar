import datetime
import pytz
import re

from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .models import UserProfile, MyCalendar, Event, Guest, EventCustomSettings
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

        if request.path not in allowed_urls and not request.user.is_authenticated():
            return redirect('my_calendar:index')
        return None


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

    all_events = profile.get_all_events()
    upcoming_events = []
    for event in all_events:
        try:
            settings = Guest.objects.get(event=event, user=profile).get_settings()[0]
        except Guest.DoesNotExist:
            settings = event.get_owner_settings()
        start = settings.start.replace(tzinfo=None)
        if start >= datetime.datetime.now():
            upcoming_events.append(event)
    context['upcoming_events'] = upcoming_events[:5]

    context['other_calendars'] = (profile.get_calendars_to_read()
        | profile.get_calendars_to_modify()).exclude(owner=profile)
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
    next_page = request.GET.get("nextpage", "my_calendar:index")
    return redirect(next_page)

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
        context['choosen_date'] = date_
        choosen_month = date_.month
        decreasing_date = date_
        while decreasing_date.month == choosen_month:
            decreasing_date -= datetime.timedelta(days=1)
        decreasing_date = decreasing_date.replace(day=1)
        context['earlier'] = decreasing_date
        increasing_date = date_
        while increasing_date.month == choosen_month:
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
        context['choosen_date'] = date_
        context['earlier'] = date_ - datetime.timedelta(days=7)
        context['later'] = date_ + datetime.timedelta(days=7)
        context['range'] = range(24)
    return render(request, 'my_calendar/week.html', context)

def day(request, year, month, day):
    context = {}
    if request.user.is_authenticated():
        try:
            date_ = datetime.date(int(year), int(month), int(day))
        except ValueError:
            date_ = datetime.datetime.now().date()
            context['date_errors'] = "You enetered wrong date."
        context['choosen_date'] = date_
        context['earlier'] = date_ - datetime.timedelta(days=1)
        context['later'] = date_ + datetime.timedelta(days=1)

        profile = get_object_or_404(UserProfile, user=request.user)
        events = profile.get_all_events()
        timezone = pytz.timezone(profile.get_timezone_display())
        context['days'] = get_events_from_days([date_], events,
            timezone, profile)
        # distinct() removes duplicates
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
            settings = EventCustomSettings()
            settings.start = pytz.utc.localize(datetime.datetime.utcnow())
            settings.end = settings.start + datetime.timedelta(minutes=30)
            timezone = get_number_and_name_of_timezone(profile)
            event_form = EventForm(data=request.POST or None, instance=settings,
                timezone=timezone)
            attending_status_form = AttendingStatusForm(data=request.POST or None)
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
    if (profile in event.calendar.modifiers.all()):

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
        context['event_form'] = event_form

        if request.method == "POST":
            form = None

            if 'save_attending_status' in request.POST:
                form = AttendingStatusForm(data=request.POST, instance=guest)
                form_name = 'attending_status_form'
            elif 'save_event' in request.POST:
                if settings_belong_to_owner:
                    event_settings = EventCustomSettings()
                    event_settings.guest = guest
                form = EventForm(data=request.POST, instance=event_settings)
                form_name = 'event_form'

            if form != None and form.is_valid():
                form.save()
                return redirect('my_calendar:event_view', event_pk=event.pk)
            elif form != None:
                context[form_name] = form

    elif profile in event.calendar.readers.all():
        if request.method == "POST":
            context['access_denied'] = ("You don't have access to "
                    + "edit this event.")
        context['event'] = event.get_owner_settings()
        context['guests'] = Guest.objects.filter(event=event)

    else:
        context['access_denied'] = "You don't have access to this event."
    return render(request, 'my_calendar/event.html', context)
