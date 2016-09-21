import datetime
import pytz

from django.contrib.auth.models import User, AnonymousUser
from django.core.urlresolvers import resolve
from django.contrib.auth import get_user
from django.test import TestCase

from .views import (index, register, profile, month, week, day,
    calendar_view, event_view)
from .models import UserProfile, MyCalendar, Event, Guest, EventCustomSettings
from .forms import RegisterForm, EventForm


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
        
    def test_template_extends_after_base(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'my_calendar/base.html')
       
    def user_registers(self):
        response = self.client.post(
            '/register', data={
                'username': 'John123',
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
        self.function = calendar_view
        
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
        
    def test_redirects_after_saving_calendar(self):
        response = self.client.post(
            self.url, data={
                'name': 'Pretty face',
                'color': '#FF0000',
        })
        calendar_ = MyCalendar.objects.first()
        self.assertRedirects(response, '/calendar/{}'.format(calendar_.pk))
        
    
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
        
    def test_passes_events_that_belong_to_calendar(self):
        event = Event.objects.create(calendar=self.calendar)
        second_calendar = MyCalendar.objects.create(owner=self.profile)
        other_event = Event.objects.create(calendar=second_calendar)
        response = self.client.get(self.url)
        self.assertIn(event, response.context['events'])
        self.assertFalse(other_event in response.context['events'])


class EventViewTest(BaseTest):
    
    def setUp(self):
        self.user_registers()
        profile = UserProfile.objects.get(user=get_user(self.client))
        self.calendar = MyCalendar.objects.create(owner=profile,
            name="Cindirella", color="E81AD4")
        self.event = Event.objects.create(calendar=self.calendar)
        self.guest = Guest.objects.create(event=self.event, user=profile)
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
                'title': 'Episode 9',
                'desc': 'Silence of slums',
                'all_day': True,
                'start_hour': '15:19',
                'start_date': '12/13/2016',
                'end_hour': '16:13',
                'end_date': '12/13/2016',
                'timezone': '374',
                'state': '1',
        })
        self.assertEqual(Event.objects.count(), 1)
        event = Event.objects.first().get_owner_settings()
        self.assertEqual(event.title, 'Episode 9')
        self.assertEqual(event.guest.state, 1)
        
    def test_cannot_save_event_with_empty_title_or_dates(self):
        title = Event.objects.first().get_owner_settings().title
        response = self.client.post(
            self.url, data={
                'title': '',
                'desc': '',
                'all_day': True,
                'start_hour': '',
                'start_date': '',
                'end_hour': '',
                'end_date': '',
                'timezone': '374',
                'state': '1',
        })
        event = Event.objects.first().get_owner_settings()
        self.assertEqual(event.title, title)
        self.assertEqual(Event.objects.count(), 1)
        self.assertIn('title', response.context['event_form'].errors)
        self.assertIn('start_hour', response.context['event_form'].errors)
        self.assertIn('start_date', response.context['event_form'].errors)
        self.assertIn('end_hour', response.context['event_form'].errors)
        self.assertIn('end_date', response.context['event_form'].errors)
              
    def test_redirects_after_saving_event(self):
        response = self.client.post(
            self.url, data={
                'title': 'Episode 9',
                'desc': 'Silence of slums',
                'all_day': True,
                'start_hour': '15:19',
                'start_date': '12/13/2016',
                'end_hour': '16:13',
                'end_date': '12/13/2016',
                'timezone': '374',
                'state': '1',
        })
        event = Event.objects.first()
        self.assertRedirects(response, '/event/{}'.format(event.pk))
        
    def test_saves_correct_date_and_hour(self):
        response = self.client.post(
            self.url, data={
                'title': 'Episode 9',
                'desc': 'Silence of slums',
                'all_day': True,
                'start_hour': '15:19',
                'start_date': '12/13/2016',
                'end_hour': '16:13',
                'end_date': '12/13/2016',
                'timezone': '374',
                'state': '1',
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
        

class NewEventTest(EventViewTest):

    def setUp(self):
        self.user_registers()
        self.profile = UserProfile.objects.get(user=get_user(self.client))
        self.calendar = MyCalendar.objects.create(owner=self.profile,
            name="Cindirella", color="E81AD4")
        self.url = '/event/new/1'
        self.template = 'my_calendar/new_event.html'
        self.function = event_view
        self.start = pytz.utc.localize(datetime.datetime.utcnow())
        self.end = self.start + datetime.timedelta(minutes=30)
        
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
                'state': '1',
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
        event = EventCustomSettings()
        europe = pytz.timezone('Europe/Warsaw')
        timezone = {
            'tz': europe,
            'number': 374,
        }
        start = europe.localize(datetime.datetime.now())
        end = europe.localize(datetime.datetime.now()
            + datetime.timedelta(minutes=30))
        form = EventForm(instance=event, start=start.astimezone(pytz.utc),
            end=end.astimezone(pytz.utc), timezone=timezone)
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
        
        
if __name__ == '__main__':
    unittest.main() 