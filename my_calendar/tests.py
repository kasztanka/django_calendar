import datetime
import pytz

from django.contrib.auth.models import User, AnonymousUser
from django.core.exceptions import ValidationError
from django.core.urlresolvers import resolve
from django.contrib.auth import get_user
from django.test import TestCase

from .views import (index, register, profile, month, week, day, new_calendar,
    calendar_view, event_view, new_event)
from .models import UserProfile, MyCalendar, Event, Guest, EventCustomSettings
from .forms import RegisterForm, EventForm, GuestForm


class BaseTest(TestCase):

    def setUp(self):
        self.url = '/'
        self.template = 'my_calendar/index.html'
        self.function = index

    def test_url_resolves_to_correct_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func, self.function)

    def test_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, self.template)
        self.assertEqual(response.status_code, 200)

    def test_template_extends_after_base(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'my_calendar/base.html')

    def user_registers(self, username="John123"):
        response = self.client.post(
            '/register', data={
                'username': username,
                'password': 'password',
                'email': 'example@email.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'timezone': '374', # 374 is 'Europe/Warsaw'
        })
        return response

class RegisterViewTest(BaseTest):

    def setUp(self):
        self.url = '/register'
        self.template = 'my_calendar/register.html'
        self.function = register

    def test_register_saves_new_user(self):
        self.user_registers()
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(UserProfile.objects.count(), 1)
        user_ = UserProfile.objects.first()
        self.assertEqual(user_.user.username, 'John123')
        self.assertEqual(user_.timezone, 374)

    def test_user_logged_in_after_registration(self):
        self.user_registers()
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated())

    def test_redirects_after_valid_registration_to_correct_profile(self):
        other_user = User.objects.create()
        other_profile = UserProfile.objects.create(user=other_user)

        response = self.user_registers()

        ## filter returns query set, so we have to take first element
        correct_profile = UserProfile.objects.filter(
            user=get_user(self.client))[0]

        self.assertRedirects(response, '/profile/{}'.format(
            correct_profile.user.username))

    def test_checks_if_timezone_exists(self):
        response = self.client.post(
            '/register', data={
                'username': 'John123',
                'password': 'password',
                'email': 'example@email.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'timezone': 'Fake timezone'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wrong timezone was chosen.")


class RegisterFormTest(TestCase):

    def test_valid_data(self):
        form = RegisterForm({
            'username': 'John123',
            'password': 'password',
            'email': 'example@email.com',
            'first_name': 'John',
            'last_name': 'Doe',
        })
        self.assertTrue(form.is_valid())

    def test_blank_data(self):
        form = RegisterForm()
        self.assertFalse(form.is_valid())


class ProfileViewTest(BaseTest):

    def setUp(self):
        correct_user = User.objects.create(username='pretty_woman')
        self.correct_profile = UserProfile.objects.create(user=correct_user)
        other_user = User.objects.create()
        self.other_profile = UserProfile.objects.create(user=other_user)
        self.url = '/profile/{}'.format(self.correct_profile.user.username)
        self.template = 'my_calendar/profile.html'
        self.function = profile

    def test_passes_correct_profile_to_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['profile'], self.correct_profile)


class LoginViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='pretty_woman', password='cow')
        self.user.set_password(self.user.password)
        self.user.save()
        profile = UserProfile.objects.create(user=self.user)
        profile.save()

    def test_user_can_login(self):
        response = self.client.post(
            '/login', data={
            'username': 'pretty_woman',
            'password': 'cow'
            }, follow=True)
        user = get_user(self.client)
        self.assertEqual(user, self.user)
        self.assertContains(response, "Hey, pretty_woman!")

    def test_passes_erros_after_wrong_login(self):
        response = self.client.post(
            '/login', data={
            'username': 'pretty_woman',
            'password': 'bull'
            })
        self.assertTrue('login_errors' in response.context)
        self.assertContains(response, "Wrong username or password.")


class LogoutViewTest(TestCase):

    def test_user_can_logout(self):
        self.client.post(
            '/register', data={
                'username': 'John123',
                'password': 'password',
                'email': 'example@email.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'timezone': '374'
        })
        user = get_user(self.client)
        self.assertNotEqual(user, None)
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)
        user = get_user(self.client)
        self.assertEqual(user, AnonymousUser())


class DayViewTest(BaseTest):

    def setUp(self):
        self.today = datetime.datetime.now().date()
        self.base_url = '/day'
        self.date_url()
        self.template = 'my_calendar/day.html'
        self.function = day

    def date_url(self):
        self.url = self.base_url + '/{}-{}-{}'.format(
            str(self.today.year), str(self.today.month), str(self.today.day))

    def passes_days_if_date_is_today(self, response):
        self.assertEqual(self.today, response.context['choosen_date'])

    def test_passes_errors_when_incorrect_date(self):
        response = self.client.get(self.base_url + '/2016-13-01')
        self.assertIn('date_errors', response.context)

    def test_passes_today_when_wrong_date(self):
        response = self.client.get(self.base_url + '/2016-13-01')
        self.passes_days_if_date_is_today(response)

    def test_passes_date(self):
        response = self.client.get(self.url)
        self.assertIn('choosen_date', response.context)

    def test_passes_calendars_when_user_logged_in(self):
        self.user_registers()
        response = self.client.get(self.url)
        self.assertIn('calendars', response.context)

    def test_passes_dict_with_data_about_events(self):
        self.user_registers()
        profile = UserProfile.objects.get(user=get_user(self.client))
        calendar = MyCalendar.objects.create(owner=profile, color="#000FFF")
        start = datetime.datetime.combine(self.today, datetime.time(13, 30))
        start = pytz.utc.localize(start)
        end = start + datetime.timedelta(minutes=30)
        event = Event.objects.create(calendar=calendar)
        guest = Guest.objects.create(event=event, user=profile)
        settings = EventCustomSettings.objects.create(guest=guest,
            start=start, end=end, all_day=False)
        response = self.client.get(self.url)
        for dict_ in response.context['days']:
            if dict_['day'] == self.today:
                dict_ = dict_['events'][0]
                break
        self.assertEqual(event.pk, dict_['pk'])
        self.assertEqual(settings.title, dict_['title'])
        self.assertEqual(settings.start, dict_['start'])
        self.assertEqual(settings.end, dict_['end'])
        self.assertEqual(settings.all_day, dict_['all_day'])
        height = (end - start).total_seconds() / (24 * 60 * 60)
        # timezone of timeline is a timezone of the user, not event
        europe = pytz.timezone(profile.get_timezone_display())
        beginning = datetime.datetime.combine(self.today, datetime.time(0))
        beginning = europe.localize(beginning)
        top = (start - beginning).total_seconds() / (24 * 60 * 60)
        self.assertEqual(height, dict_['height'])
        self.assertEqual(top, dict_['top'])
        self.assertEqual(calendar.color, dict_['color'])
        self.assertEqual(calendar.pk, dict_['class'])

    def test_event_height_when_time_change(self):
        self.user_registers()
        profile = UserProfile.objects.get(user=get_user(self.client))
        calendar = MyCalendar.objects.create(owner=profile, color="#000FFF")
        europe = pytz.timezone(profile.get_timezone_display())
        time_change = datetime.date(2016, 10, 30)
        start = datetime.datetime.combine(time_change, datetime.time(0, 0))
        start = europe.localize(start)
        end = datetime.datetime.combine(time_change, datetime.time(4, 0))
        end = europe.localize(end)
        event = Event.objects.create(calendar=calendar)
        guest = Guest.objects.create(event=event, user=profile)
        settings = EventCustomSettings.objects.create(guest=guest,
            start=start, end=end, all_day=False)
        response = self.client.get(self.base_url + '/2016-10-30')
        for dict_ in response.context['days']:
            if dict_['day'] == time_change:
                dict_ = dict_['events'][0]
                break
        height = (4 * 3600) / (24 * 60 * 60)
        self.assertEqual(height, dict_['height'])


class MonthViewTest(DayViewTest):

    def setUp(self):
        self.today = datetime.datetime.now().date()
        self.base_url = '/month'
        self.date_url()
        self.template = 'my_calendar/month.html'
        self.function = month

    def passes_days_if_date_is_today(self, response):
        first = datetime.date(self.today.year, self.today.month, 1)
        some = datetime.date(self.today.year, self.today.month, 25)
        self.assertIn(first, response.context['days'])
        self.assertIn(some, response.context['days'])

    def test_passes_days_of_month_in_context(self):
        response = self.client.get(self.url)
        self.passes_days_if_date_is_today(response)

    def test_passes_correct_days_when_month_given(self):
        response = self.client.get(self.base_url + '/2015-02-01')
        first = datetime.date(2015, 1, 26)
        last = datetime.date(2015, 3, 1)
        self.assertIn(first, response.context['days'])
        self.assertIn(last, response.context['days'])
        self.assertEqual(len(response.context['days']), 35)

class WeekViewTest(DayViewTest):

    def setUp(self):
        self.today = datetime.datetime.now().date()
        self.base_url = '/week'
        self.date_url()
        self.template = 'my_calendar/week.html'
        self.function = week

    def passes_days_if_date_is_today(self, response):
        previous = self.today - datetime.timedelta(days=1)
        next = self.today + datetime.timedelta(days=1)
        self.assertTrue(previous in response.context['days']
            or next in response.context['days'])

    def test_passes_days_of_week_in_context(self):
        response = self.client.get(self.url)
        self.passes_days_if_date_is_today(response)

    def test_passes_correct_days_when_week_given(self):
        response = self.client.get(self.base_url + '/2015-02-01')
        first = datetime.date(2015, 1, 26)
        last = datetime.date(2015, 2, 1)
        self.assertIn(first, response.context['days'])
        self.assertIn(last, response.context['days'])
        self.assertEqual(len(response.context['days']), 7)


class NewCalendarTest(BaseTest):

    def setUp(self):
        self.user_registers()
        self.url = '/calendar/new'
        self.template = 'my_calendar/new_calendar.html'
        self.function = new_calendar

    def test_saves_calendar(self):
        self.client.post(
            self.url, data={
                'name': 'Pretty face',
                'color': '#FF0000',
        })
        self.assertEqual(MyCalendar.objects.count(), 1)
        self.assertEqual(MyCalendar.objects.first().name, 'Pretty face')

    def test_cannot_save_empty_calendar(self):
        response = self.client.post(
            self.url, data={
                'name': '',
                'color': '#FF0000',
        })
        self.assertEqual(MyCalendar.objects.count(), 0)
        self.assertIn('errors', response.context)

    def test_checks_color_regex(self):
        calendars_amount = MyCalendar.objects.count()
        response = self.client.post(
            self.url, data={
                'name': 'Name',
                'color': '#FF000',
        })
        self.assertIn('errors', response.context)
        response = self.client.post(
            self.url, data={
                'name': 'Name',
                'color': '#FF0ZZZ',
        })
        self.assertIn('errors', response.context)
        response = self.client.post(
            self.url, data={
                'name': 'Name',
                'color': '2FFE000',
        })
        self.assertIn('errors', response.context)
        self.assertEqual(MyCalendar.objects.count(), calendars_amount)

    def test_after_saving_calendar_goes_to_its_site(self):
        response = self.client.post(
            self.url, data={
                'name': 'Pretty face',
                'color': '#FF0000',
        })
        calendar_ = MyCalendar.objects.first()
        self.assertRedirects(response, '/calendar/{}'.format(calendar_.pk))

    def test_passes_calendar_form(self):
        response = self.client.get(self.url)
        self.assertIn('calendar_form', response.context)

    def test_saves_can_read_and_can_modify_users(self):
        profile = UserProfile.objects.get(user=get_user(self.client))
        response = self.client.post(
            self.url, data={
                'name': 'Pretty face',
                'color': '#FF0000',
                'can_read': ['1'],
                'can_modify': ['1'],
        })
        calendar_ = MyCalendar.objects.first()
        self.assertEqual(list(calendar_.can_read.all())[0], profile)
        self.assertEqual(list(calendar_.can_modify.all())[0], profile)

    def test_cannot_save_not_existing_user(self):
        calendar_amount = MyCalendar.objects.count()
        profile = UserProfile.objects.get(user=get_user(self.client))
        response = self.client.post(
            self.url, data={
                'name': 'Pretty face',
                'color': '#FF0000',
                'can_read': ['2'],
                'can_modify': ['2'],
        })
        self.assertEqual(calendar_amount, MyCalendar.objects.count())
        if calendar_amount:
            calendar_ = MyCalendar.objects.first()
            self.assertEqual(list(calendar_.can_read.all()), [])
            self.assertEqual(list(calendar_.can_modify.all()), [])


class CalendarViewTest(NewCalendarTest):

    def setUp(self):
        self.user_registers()
        self.profile = UserProfile.objects.get(user=get_user(self.client))
        self.calendar = MyCalendar.objects.create(owner=self.profile,
            name="Cindirella", color="E81AD4")
        self.url = '/calendar/1'
        self.template = 'my_calendar/calendar.html'
        self.function = calendar_view

    def test_cannot_save_empty_calendar(self):
        name = MyCalendar.objects.first().name
        response = self.client.post(
            self.url, data={
                'name': '',
                'color': '#FF0000',
        })
        calendar_ = MyCalendar.objects.first()
        self.assertEqual(calendar_.name, name)
        self.assertEqual(MyCalendar.objects.count(), 1)
        self.assertIn('errors', response.context)

    def test_after_saving_calendar_goes_to_its_site(self):
        response = self.client.post(
            self.url, data={
                'name': 'Pretty face',
                'color': '#FF0000',
        })
        calendar_ = MyCalendar.objects.first()
        self.assertEqual(response.request['PATH_INFO'], self.url)

    def test_passes_events_that_belong_to_calendar(self):
        event = Event.objects.create(calendar=self.calendar)
        second_calendar = MyCalendar.objects.create(owner=self.profile)
        other_event = Event.objects.create(calendar=second_calendar)
        response = self.client.get(self.url)
        self.assertIn(event, response.context['events'])
        self.assertFalse(other_event in response.context['events'])


class NewEventTest(BaseTest):

    def setUp(self):
        self.user_registers()
        self.profile = UserProfile.objects.get(user=get_user(self.client))
        self.calendar = MyCalendar.objects.create(owner=self.profile,
            name="Cindirella", color="E81AD4")
        self.url = '/event/new/1'
        self.template = 'my_calendar/new_event.html'
        self.function = new_event
        self.start = pytz.utc.localize(datetime.datetime.utcnow())
        self.end = self.start + datetime.timedelta(minutes=30)

    def test_saves_event(self):
        self.client.post(
            self.url, data={
                'save_event':1,
                'title': 'Episode 9',
                'desc': 'Silence of slums',
                'all_day': True,
                'start_hour': '15:19',
                'start_date': '12/13/2016',
                'end_hour': '16:13',
                'end_date': '12/13/2016',
                'timezone': '374',
                'attending_status': '1',
        })
        self.assertEqual(Event.objects.count(), 1)
        event = Event.objects.first().get_owner_settings()
        self.assertEqual(event.title, 'Episode 9')
        self.assertEqual(event.guest.attending_status, 1)

    def test_redirects_after_saving_event(self):
        response = self.client.post(
            self.url, data={
                'save_event':1,
                'title': 'Episode 9',
                'desc': 'Silence of slums',
                'all_day': True,
                'start_hour': '15:19',
                'start_date': '12/13/2016',
                'end_hour': '16:13',
                'end_date': '12/13/2016',
                'timezone': '374',
                'attending_status': '1',
        })
        event = Event.objects.first()
        self.assertRedirects(response, '/event/{}'.format(event.pk))

    def test_saves_correct_date_and_hour(self):
        response = self.client.post(
            self.url, data={
                'save_event':1,
                'title': 'Episode 9',
                'desc': 'Silence of slums',
                'all_day': True,
                'start_hour': '15:19',
                'start_date': '12/13/2016',
                'end_hour': '16:13',
                'end_date': '12/13/2016',
                'timezone': '374',
                'attending_status': '1',
            }, follow=True)
        europe = pytz.timezone('Europe/Warsaw')
        utc = pytz.timezone('UTC')
        start = datetime.datetime(2016, 12, 13, 15, 19)
        start = europe.localize(start).astimezone(utc)
        end = datetime.datetime(2016, 12, 13, 16, 13)
        end = europe.localize(end).astimezone(utc)
        event = Event.objects.first().get_owner_settings()
        self.assertContains(response, '15:19')
        self.assertEqual(event.start, start)
        self.assertContains(response, '16:13')
        self.assertEqual(event.end, end)

    def test_cannot_save_event_with_empty_title_or_dates(self):
        response = self.client.post(
            self.url, data={
                'title': '',
                'desc': 'Silence of slums',
                'all_day': True,
                'start_hour': '',
                'start_date': '',
                'end_hour': '',
                'end_date': '',
                'timezone': '374',
                'attending_status': '1',
        })
        self.assertEqual(Event.objects.count(), 0)
        self.assertIn('title', response.context['event_form'].errors)
        self.assertIn('start_hour', response.context['event_form'].errors)
        self.assertIn('start_date', response.context['event_form'].errors)
        self.assertIn('end_hour', response.context['event_form'].errors)
        self.assertIn('end_date', response.context['event_form'].errors)

    def test_passes_correct_initial_timezone_and_datetime(self):
        response = self.client.get(self.url)
        form = response.context['event_form']
        user_timezone = self.profile.get_timezone_display()
        start = self.start.astimezone(pytz.timezone(user_timezone))
        end = self.end.astimezone(pytz.timezone(user_timezone))
        self.assertEqual(form.initial['start_date'], start.strftime('%m/%d/%Y'))
        self.assertEqual(form.initial['start_hour'], start.strftime('%H:%M'))
        self.assertEqual(form.initial['end_date'], end.strftime('%m/%d/%Y'))
        self.assertEqual(form.initial['end_hour'], end.strftime('%H:%M'))
        event = EventCustomSettings(timezone=form.initial['timezone'])
        self.assertEqual(user_timezone, event.get_timezone_display())

    def test_others_cannot_save_event(self):
        amount = Event.objects.count()
        response = self.client.get('/logout')
        self.user_registers(username="Other")
        response = self.client.post(
            self.url, data={
                'save_event':1,
                'title': 'Episode 9',
                'desc': 'Silence of slums',
                'all_day': True,
                'start_hour': '15:19',
                'start_date': '12/13/2016',
                'end_hour': '16:13',
                'end_date': '12/13/2016',
                'timezone': '374',
                'attending_status': '1',
        })
        self.assertEqual(amount, Event.objects.count())
        if amount:
            settings = Event.objects.first().get_owner_settings()
            self.assertEqual(settings.title, 'Radio Gaga')
            self.assertEqual(response.context['access_denied'],
                "You don't have access to this event.")
        profile = UserProfile.objects.get(user=get_user(self.client))
        # users that can read others calendars_amount
        # also shouldn't have access to modifications of events
        self.calendar.can_read.add(profile)
        response = self.client.post(
            self.url, data={
                'save_event':1,
                'title': 'Episode 9',
                'desc': 'Silence of slums',
                'all_day': True,
                'start_hour': '15:19',
                'start_date': '12/13/2016',
                'end_hour': '16:13',
                'end_date': '12/13/2016',
                'timezone': '374',
                'attending_status': '1',
        })
        self.assertEqual(amount, Event.objects.count())
        if amount:
            settings = Event.objects.first().get_owner_settings()
            self.assertEqual(settings.title, 'Radio Gaga')
            self.assertEqual(response.context['access_denied'],
                "You don't have access to edit this event.")
        else:
            self.assertEqual(response.context['access_denied'],
                "You don't have access to add events to this calendar.")

    def test_user_with_modify_can_edit_but_not_create_event(self):
        amount = Event.objects.count()
        response = self.client.get('/logout')
        self.user_registers(username="Other")
        profile = UserProfile.objects.get(user=get_user(self.client))
        self.calendar.can_modify.add(profile)
        response = self.client.post(
            self.url, data={
                'save_event':1,
                'title': 'Episode 9',
                'desc': 'Silence of slums',
                'all_day': True,
                'start_hour': '15:19',
                'start_date': '12/13/2016',
                'end_hour': '16:13',
                'end_date': '12/13/2016',
                'timezone': '374',
                'attending_status': '1',
        })
        self.assertEqual(amount, Event.objects.count())
        if amount:
            settings = Event.objects.first().get_owner_settings()
            self.assertEqual(settings.title, 'Episode 9')
        else:
            self.assertEqual(response.context['access_denied'],
                "You don't have access to add events to this calendar.")


class EventViewTest(NewEventTest):

    def setUp(self):
        self.user_registers()
        profile = UserProfile.objects.get(user=get_user(self.client))
        self.calendar = MyCalendar.objects.create(owner=profile,
            name="Cindirella", color="E81AD4")
        self.event = Event.objects.create(calendar=self.calendar)
        self.guest = Guest.objects.create(event=self.event, user=profile,
            attending_status=Guest.MAYBE)
        self.start = pytz.utc.localize(datetime.datetime.utcnow())
        self.end = self.start + datetime.timedelta(minutes=30)
        self.settings = EventCustomSettings.objects.create(
            guest=self.guest, title='Radio Gaga', desc='Radio Blabla',
            timezone=374, start=self.start, end=self.end, all_day=True)
        self.url = '/event/1'
        self.template = 'my_calendar/event.html'
        self.function = event_view

    def test_saves_event(self):
        self.client.post(
            self.url, data={
                'save_event':1,
                'title': 'Episode 9',
                'desc': 'Silence of slums',
                'all_day': True,
                'start_hour': '15:19',
                'start_date': '12/13/2016',
                'end_hour': '16:13',
                'end_date': '12/13/2016',
                'timezone': '374',
                'attending_status': '1',
        })
        self.assertEqual(Event.objects.count(), 1)
        event = Event.objects.first().get_owner_settings()
        self.assertEqual(event.title, 'Episode 9')
        self.assertNotEqual(event.guest.attending_status, 1)

    def test_cannot_save_event_with_empty_title_or_dates(self):
        title = Event.objects.first().get_owner_settings().title
        response = self.client.post(
            self.url, data={
                'save_event':1,
                'title': '',
                'desc': '',
                'all_day': True,
                'start_hour': '',
                'start_date': '',
                'end_hour': '',
                'end_date': '',
                'timezone': '374',
                'attending_status': '1',
        })
        event = Event.objects.first().get_owner_settings()
        self.assertEqual(event.title, title)
        self.assertEqual(Event.objects.count(), 1)
        self.assertIn('title', response.context['event_form'].errors)
        self.assertIn('start_hour', response.context['event_form'].errors)
        self.assertIn('start_date', response.context['event_form'].errors)
        self.assertIn('end_hour', response.context['event_form'].errors)
        self.assertIn('end_date', response.context['event_form'].errors)

    def test_passes_correct_initial_timezone_and_datetime(self):
        response = self.client.get(self.url)
        form = response.context['event_form']
        timezone = pytz.timezone(self.settings.get_timezone_display())
        start = self.start.astimezone(timezone)
        end = self.end.astimezone(timezone)
        self.assertEqual(form.initial['start_date'], start.strftime('%m/%d/%Y'))
        self.assertEqual(form.initial['start_hour'], start.strftime('%H:%M'))
        self.assertEqual(form.initial['end_date'], end.strftime('%m/%d/%Y'))
        self.assertEqual(form.initial['end_hour'], end.strftime('%H:%M'))
        self.assertEqual(self.settings.timezone, form.initial['timezone'])

    def test_saves_guest(self):
        self.client.get('/logout')
        self.user_registers(username="Human")
        self.client.get('/logout')
        self.client.post(
            '/login', data={
            'username': 'John123',
            'password': 'password'
            })
        self.client.post(self.url, data={
            'save_guest': 1,
            'user': 2,
        })
        self.assertEqual(Guest.objects.count(), 2)
        guest = Guest.objects.get(pk=2)
        user = UserProfile.objects.get(pk=2)
        self.assertEqual(guest.user, user)
        self.assertEqual(guest.event, self.event)

    def test_cannot_save_same_guest_for_event(self):
        self.client.get('/logout')
        self.user_registers(username="Human")
        self.client.get('/logout')
        self.client.post(
            '/login', data={
            'username': 'John123',
            'password': 'password'
            })
        response = self.client.post(self.url, data={
            'save_guest': 1,
            'user': 1,
        })
        self.assertEqual(Guest.objects.count(), 1)
        self.assertEqual(response.context['guest_form'].errors['user'],
            ["This user is already guest added to this event."])

    def test_attending_status_form_in_context_when_guest(self):
        response = self.client.get(self.url)
        self.assertIn('attending_status_form', response.context)
        form = response.context['attending_status_form']
        self.assertEqual(form.initial['attending_status'], Guest.MAYBE)

        self.client.get('/logout')
        self.user_registers(username="Human")
        profile = UserProfile.objects.get(user=get_user(self.client))
        Guest.objects.create(user=profile, event=self.event)
        response = self.client.get(self.url)
        self.assertIn('attending_status_form', response.context)
        form = response.context['attending_status_form']
        self.assertEqual(form.initial['attending_status'], Guest.UNKNOWN)

        self.client.get('/logout')
        self.user_registers(username="Human")
        response = self.client.get(self.url)
        self.assertFalse('attending_status_form' in response.context)

    def test_guest_can_see_event(self):
        self.client.get('/logout')
        self.user_registers(username="Human")
        profile = UserProfile.objects.get(user=get_user(self.client))
        Guest.objects.create(user=profile, event=self.event)

        response = self.client.get(self.url)
        self.assertIn('event', response.context)
        self.assertIn('guests', response.context)
        self.assertIn('user_is_guest', response.context)
        self.assertIn('event_form', response.context)
        self.assertIn('guest_message', response.context)

    def test_saves_attending_status(self):
        response = self.client.post(
            self.url, data={
                'save_attending_status':1,
                'attending_status': '1',
        })
        self.assertEqual(Guest.objects.first().attending_status, 1)

        self.client.get('/logout')
        self.user_registers(username="Human")
        profile = UserProfile.objects.get(user=get_user(self.client))
        Guest.objects.create(user=profile, event=self.event)

        response = self.client.post(
            self.url, data={
                'save_attending_status':1,
                'attending_status': '4',
        })
        guest = Guest.objects.get(user=profile, event=self.event)
        self.assertEqual(guest.attending_status, 4)

    def test_guest_can_change_his_settings(self):
        self.client.get('/logout')
        self.user_registers(username="Human")
        profile = UserProfile.objects.get(user=get_user(self.client))
        guest = Guest.objects.create(user=profile, event=self.event)

        # at first guest creates new object
        # then he changes this object
        for i in range(2):
            response = self.client.post(
                self.url, data={
                    'save_event':1,
                    'title': ('Hello' + str(i)),
                    'desc': 'World',
                    'all_day': True,
                    'start_hour': '15:19',
                    'start_date': '12/13/2016',
                    'end_hour': '16:13',
                    'end_date': '12/13/2016',
                    'timezone': '374',
                    'attending_status': '1',
            })
            self.assertEqual(EventCustomSettings.objects.count(), 2)
            settings = EventCustomSettings.objects.get(guest=guest)
            self.assertEqual(settings.title, 'Hello' + str(i))


class EventFormTest(TestCase):

    def test_datetime_inputs_have_css_classes(self):
        form = EventForm()
        self.assertIn('class="datepicker" id="id_start_date"', form.as_p())
        self.assertIn('class="time" id="id_start_hour"', form.as_p())
        self.assertIn('class="datepicker" id="id_end_date"', form.as_p())
        self.assertIn('class="time" id="id_end_hour"', form.as_p())

    def test_valid_data(self):
        form = EventForm({
            'title': 'Episode 9',
            'desc': 'Silence of slums',
            'all_day': True,
            'start_hour': '15:19',
            'start_date': '12/13/2016',
            'end_hour': '16:13',
            'end_date': '12/13/2016',
            'timezone': '374',
        })
        self.assertTrue(form.is_valid())

    def test_blank_title(self):
        form = EventForm()
        self.assertFalse(form.is_valid())

    def test_no_description_is_valid(self):
        form = EventForm({
            'title': 'Episode 9',
            'desc': '',
            'all_day': True,
            'start_hour': '15:19',
            'start_date': '12/13/2016',
            'end_hour': '16:13',
            'end_date': '12/13/2016',
            'timezone': '374'
        })
        self.assertTrue(form.is_valid())

    def test_end_before_start_not_valid(self):
        form = EventForm({
            'title': 'Episode 9',
            'desc': 'Bla',
            'start_hour': '16:19',
            'start_date': '12/13/2016',
            'end_hour': '16:13',
            'end_date': '12/13/2016',
            'timezone': '374'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('end_date', form.errors)

    def test_hours_skipped_in_validation_when_all_day_event(self):
        form = EventForm({
            'title': 'Episode 9',
            'desc': 'Bla',
            'all_day': True,
            'start_hour': '16:19',
            'start_date': '12/13/2016',
            'end_hour': '16:13',
            'end_date': '12/13/2016',
            'timezone': '374'
        })
        self.assertTrue(form.is_valid())

    def test_validation_works_when_hours_skipped(self):
        form = EventForm({
            'title': 'Episode 9',
            'desc': 'Bla',
            'all_day': True,
            'start_hour': '16:19',
            'start_date': '12/13/2016',
            'end_hour': '16:13',
            'end_date': '12/11/2016',
            'timezone': '374'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('end_date', form.errors)

    def test_inital_datetime_correct_when_timezone_given(self):
        europe = pytz.timezone('Europe/Warsaw')
        timezone = {
            'tz': europe,
            'number': 374,
        }
        start = europe.localize(datetime.datetime.now())
        end = europe.localize(datetime.datetime.now()
            + datetime.timedelta(minutes=30))
        event = EventCustomSettings(start=start, end=end)
        form = EventForm(instance=event, timezone=timezone)
        self.assertEqual(form.initial['start_date'], start.strftime('%m/%d/%Y'))
        self.assertEqual(form.initial['start_hour'], start.strftime('%H:%M'))
        self.assertEqual(form.initial['end_date'], end.strftime('%m/%d/%Y'))
        self.assertEqual(form.initial['end_hour'], end.strftime('%H:%M'))
        self.assertEqual(form.initial['timezone'], timezone['number'])

    def test_checks_timezone(self):
        tz_len = len(pytz.common_timezones_set)
        form = EventForm({
            'title': 'Episode 9',
            'desc': 'Bla',
            'all_day': True,
            'start_hour': '16:19',
            'start_date': '12/13/2016',
            'end_hour': '16:13',
            'end_date': '12/14/2016',
            'timezone': str(tz_len + 10),
        })
        self.assertFalse(form.is_valid())
        self.assertIn("Wrong timezone was chosen.", form.errors['timezone'])


class EventCustomSettingsTest(TestCase):

    def test_default_timezone_utc(self):
        event = EventCustomSettings()
        self.assertEqual(event.get_timezone_display(), str(pytz.utc))

    def test_unique_guest_for_settings(self):
        user = User.objects.create(username='John')
        profile = UserProfile.objects.create(user=user)
        calendar = MyCalendar.objects.create(owner=profile)
        event = Event.objects.create(calendar=calendar)
        guest =  Guest.objects.create(user=profile, event=event)
        start = pytz.utc.localize(datetime.datetime.now())
        end = start + datetime.timedelta(minutes=30)
        EventCustomSettings.objects.create(guest=guest, start=start, end=end,
            title="Some title", all_day=True)
        start = datetime.datetime.now()
        end = start + datetime.timedelta(minutes=30)
        with self.assertRaises(ValidationError):
            settings2 = EventCustomSettings(guest=guest, start=start, end=end,
                title='Habubaba', all_day=True)
            settings2.full_clean()


class GuestFormTest(TestCase):

    def setUp(self):
        user_ = User.objects.create(username="Owner")
        self.profile = UserProfile.objects.create(user=user_)
        calendar = MyCalendar.objects.create(owner=self.profile,
            name="Cindirella", color="E81AD4")
        self.event = Event.objects.create(calendar=calendar)

    def user_registers(self, username="John123"):
        response = self.client.post(
            '/register', data={
                'username': username,
                'password': 'password',
                'email': 'example@email.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'timezone': '374', # 374 is 'Europe/Warsaw'
        })
        return response

    def test_valid_data(self):
        self.user_registers()
        form = GuestForm(event=self.event, data={'user': 1})
        self.assertTrue(form.is_valid())

    def test_wrong_data(self):
        # not existing user
        form = GuestForm(event=self.event, data={'user': 2})
        self.assertFalse(form.is_valid())
        # empty data
        form = GuestForm(event=self.event, data={})
        self.assertFalse(form.is_valid())

    def test_form_validation_duplicate_guests(self):
        Guest.objects.create(event=self.event, user=self.profile)
        form = GuestForm(event=self.event, data={'user': 1})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['user'], [("This user is already guest "
            + "added to this event.")])


class GuestTest(TestCase):

    def test_duplicates_invalid(self):
        user = User.objects.create(username="Owner")
        profile = UserProfile.objects.create(user=user)
        calendar = MyCalendar.objects.create(owner=profile,
            name="Cindirella", color="E81AD4")
        event = Event.objects.create(calendar=calendar)
        Guest.objects.create(event=event, user=profile)
        with self.assertRaises(ValidationError):
            guest = Guest(event=event, user=profile)
            guest.full_clean()

if __name__ == '__main__':
    unittest.main()
