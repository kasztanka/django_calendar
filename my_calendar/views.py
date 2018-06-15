import datetime
import pytz
import re

from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib.postgres.search import SearchVector
from django.contrib.auth.models import User
from django.views import View

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

class RegisterView(View):
    template_name  = 'my_calendar/register.html'
    context = {}

    def prepare_forms(self, data=None):
        self.register_form = RegisterForm(data=data)
        self.profile_form = ProfileForm(data=data)
        self.context['register_form'] = self.register_form
        self.context['profile_form'] = self.profile_form

    def get(self, request):
        self.prepare_forms()
        return render(request, self.template_name, self.context)

    def post(self, request):
        self.prepare_forms(request.POST)
        if self.register_form.is_valid() and self.profile_form.is_valid():
            user = self.register_form.save()
            unhashed_password = user.password
            user.set_password(user.password)
            user.save()
            profile = self.profile_form.save(commit=False)
            profile.user = user
            profile.save()
            user_obj = authenticate(username=user.username,
                password=unhashed_password)
            login(request, user_obj)
            return redirect('my_calendar:profile', username=user.username)
        else:
            return render(request, self.template_name, self.context)


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

def month(request, date):
    context = {}
    if request.user.is_authenticated():
        try:
            date_ = datetime.datetime.strptime(date, "%Y-%m-%d").date()
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

def week(request, date):
    context = {}
    if request.user.is_authenticated():
        try:
            date_ = datetime.datetime.strptime(date, "%Y-%m-%d").date()
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

def day(request, date):
    context = {}
    if request.user.is_authenticated():
        try:
            date_ = datetime.datetime.strptime(date, "%Y-%m-%d").date()
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
            if calendar_form.is_valid():
                calendar_ = calendar_form.save()
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
                    if calendar_form.is_valid():
                        calendar_ = calendar_form.save()
                        return redirect('my_calendar:calendar_view',
                            cal_pk=calendar_.pk)
                context['calendar_form'] = calendar_form
            context['calendar'] = calendar_
            events = Event.objects.filter(calendar=calendar_)
            context['events'] = events
        else:
            context['access_denied'] = "You don't have access to this calendar."
    return render(request, 'my_calendar/calendar.html', context)

def new_event(request):
    context = {}
    if request.user.is_authenticated():
        profile = get_object_or_404(UserProfile, user=request.user)
        event = Event()
        event.start = pytz.utc.localize(datetime.datetime.utcnow())
        event.end = event.start + datetime.timedelta(minutes=30)
        if request.GET.get('cal_pk'):
            cal_pk = request.GET.get('cal_pk')
            calendar = MyCalendar.objects.filter(pk=cal_pk).first()
            if calendar and profile in calendar.modifiers.all():
                event.calendar = calendar
        timezone = get_number_and_name_of_timezone(profile)
        event_form = EventForm(data=request.POST or None, user=profile,
            instance=event, timezone=timezone)
        attending_status_form = AttendingStatusForm(data=request.POST or None)
        if request.method == "POST":
            if event_form.is_valid(user=profile) and attending_status_form.is_valid():
                event = event_form.save()
                guest = attending_status_form.save(commit=False)
                guest.event = event
                guest.user = profile
                guest.save()
                return redirect('my_calendar:event_view', event_pk=event.pk)
        context['event_form'] = event_form
        context['attending_status_form'] = attending_status_form
    return render(request, 'my_calendar/new_event.html', context)

def event_view(request, event_pk, event_form=None):
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
        pass

    if 'form_errors' in request.session:
        context['form_errors'] = request.session.pop('form_errors')
        context['non_field_errors'] = request.session.pop('non_field_errors')
        context['invalid_form'] = request.session.pop('invalid_form')

    if event in profile.get_all_events():
        context['event'] = event
        context['guests'] = Guest.objects.filter(event=event)
        if profile in event.calendar.modifiers.all():
            timezone = get_number_and_name_of_timezone(event)
            context['event_form'] = EventForm(user=profile, instance=event, timezone=timezone)
            context['guest_form'] = GuestForm(event=event)
    else:
        context['access_denied'] = "You don't have access to this event."
    return render(request, 'my_calendar/event.html', context)

def edit_event(request, event_pk):
    context = {}
    if request.user.is_authenticated():
        event = get_object_or_404(Event, pk=event_pk)
        profile = get_object_or_404(UserProfile, user=request.user)
        if profile in event.calendar.modifiers.all():
            if request.method == "POST":
                form = EventForm(data=request.POST, user=profile, instance=event)
                if form.is_valid(user=profile):
                    form.save()
                else:
                    request.session['form_errors'] = form.errors
                    request.session['non_field_errors'] = form.non_field_errors()
                    request.session['invalid_form'] = 'editing event'
                return redirect('my_calendar:event_view', event_pk=event.pk)
        else:
            context['access_denied'] = "You don't have access to modify this event."
    return render(request, 'my_calendar/event.html', context)

def add_guest(request, event_pk):
    context = {}
    if request.user.is_authenticated():
        event = get_object_or_404(Event, pk=event_pk)
        profile = get_object_or_404(UserProfile, user=request.user)
        if profile in event.calendar.modifiers.all():
            if request.method == "POST":
                form = GuestForm(data=request.POST, event=event)
                if form.is_valid():
                    form.save()
                else:
                    request.session['form_errors'] = form.errors
                    request.session['non_field_errors'] = form.non_field_errors()
                    request.session['invalid_form'] = 'editing event'
                return redirect('my_calendar:event_view', event_pk=event.pk)
        else:
            context['access_denied'] = "You don't have access to modify this event."
    return render(request, 'my_calendar/event.html', context)

def rsvp_to_event(request, event_pk):
    context = {}
    if request.user.is_authenticated():
        event = get_object_or_404(Event, pk=event_pk)
        profile = get_object_or_404(UserProfile, user=request.user)
        try:
            guest = Guest.objects.get(event=event, user=profile)
            if request.method == "POST":
                form = AttendingStatusForm(data=request.POST, instance=guest)
                if form.is_valid():
                    form.save()
                else:
                    request.session['form_errors'] = form.errors
                    request.session['non_field_errors'] = form.non_field_errors()
                    request.session['invalid_form'] = 'editing event'
                return redirect('my_calendar:event_view', event_pk=event.pk)
        except Guest.DoesNotExist:
            context['access_denied'] = "You don't have access to modify this event."
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
