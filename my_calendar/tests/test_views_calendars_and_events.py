import datetime
import pytz

from django.contrib.auth.models import User
from django.contrib.auth import get_user

from my_calendar.views import new_calendar, calendar_view, event_view, new_event
from my_calendar.models import (UserProfile, MyCalendar, Event, Guest)
from .test_views_base import BaseViewTest


class NewCalendarViewTest(BaseViewTest):

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
        self.assertTrue(response.context['calendar_form'].errors)

    def test_checks_color_regex(self):
        calendars_amount = MyCalendar.objects.count()
        response = self.client.post(
            self.url, data={
                'name': 'Name',
                'color': '#FF000',
        })
        self.assertTrue(response.context['calendar_form'].errors)
        response = self.client.post(
            self.url, data={
                'name': 'Name',
                'color': '#FF0ZZZ',
        })
        self.assertTrue(response.context['calendar_form'].errors)
        response = self.client.post(
            self.url, data={
                'name': 'Name',
                'color': '2FFE000',
        })
        self.assertTrue(response.context['calendar_form'].errors)
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

    def test_saves_readers_and_modifiers(self):
        user_2 = User.objects.create(username="Other")
        profile = UserProfile.objects.create(user=user_2)
        response = self.client.post(
            self.url, data={
                'name': 'Pretty face',
                'color': '#FF0000',
                'readers': ['2'],
                'modifiers': ['2'],
        })
        calendar_ = MyCalendar.objects.first()
        self.assertIn(profile, calendar_.readers.all())
        self.assertIn(profile, calendar_.modifiers.all())

    def test_cannot_save_not_existing_user(self):
        calendar_amount = MyCalendar.objects.count()
        profile = UserProfile.objects.get(user=get_user(self.client))
        response = self.client.post(
            self.url, data={
                'name': 'Pretty face',
                'color': '#FF0000',
                'readers': ['2'],
                'modifiers': ['2'],
        })
        self.assertEqual(calendar_amount, MyCalendar.objects.count())
        if calendar_amount:
            calendar_ = MyCalendar.objects.first()
            self.assertEqual(list(calendar_.readers.all()), [profile])
            self.assertEqual(list(calendar_.modifiers.all()), [profile])

    def test_owner_by_default_in_modifiers_and_readers(self):
        # test only for new_event view
        if MyCalendar.objects.count():
            return
        profile = UserProfile.objects.get(user=get_user(self.client))
        response = self.client.post(
            self.url, data={
                'name': 'Pretty face',
                'color': '#FF0000',
        })
        calendar_ = MyCalendar.objects.first()
        self.assertIn(profile, calendar_.readers.all())
        self.assertIn(profile, calendar_.modifiers.all())

    def test_owner_not_selectable_in_modifiers_and_readers(self):
        profile = UserProfile.objects.get(user=get_user(self.client))
        response = self.client.get(self.url)
        calendar_form = response.context['calendar_form']
        self.assertNotIn(profile, calendar_form.fields['readers'].queryset)
        self.assertNotIn(profile, calendar_form.fields['modifiers'].queryset)


class CalendarViewTest(NewCalendarViewTest):

    def setUp(self):
        self.user_registers()
        self.profile = UserProfile.objects.get(user=get_user(self.client))
        self.calendar = MyCalendar.objects.create(owner=self.profile,
            name="Cindirella", color="E81AD4")
        self.calendar.readers.add(self.calendar.owner)
        self.calendar.modifiers.add(self.calendar.owner)
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
        self.assertIn('name', response.context['calendar_form'].errors)

    def test_after_saving_calendar_goes_to_its_site(self):
        response = self.client.post(
            self.url, data={
                'name': 'Pretty face',
                'color': '#FF0000',
        })
        calendar_ = MyCalendar.objects.first()
        self.assertEqual(response.request['PATH_INFO'], self.url)

    def test_passes_events_that_belong_to_calendar(self):
        start = pytz.utc.localize(datetime.datetime.now())
        end = start + datetime.timedelta(minutes=30)
        event = Event.objects.create(calendar=self.calendar, start=start, end=end,
            title="Some title", all_day=True)
        second_calendar = MyCalendar.objects.create(owner=self.profile)
        other_event = Event.objects.create(calendar=second_calendar, start=start, end=end,
            title="Some title", all_day=True)
        response = self.client.get(self.url)
        self.assertIn(event, response.context['events'])
        self.assertFalse(other_event in response.context['events'])


class NewEventViewTest(BaseViewTest):

    def setUp(self):
        self.user_registers()
        self.profile = UserProfile.objects.get(user=get_user(self.client))
        self.calendar = MyCalendar.objects.create(owner=self.profile,
            name="Cindirella", color="E81AD4")
        self.calendar.readers.add(self.calendar.owner)
        self.calendar.modifiers.add(self.calendar.owner)
        self.url = self.save_event_url = '/event/new'
        self.template = 'my_calendar/new_event.html'
        self.function = new_event
        self.start = pytz.utc.localize(datetime.datetime.utcnow())
        self.end = self.start + datetime.timedelta(minutes=30)

    def test_saves_event(self):
        self.client.post(
            self.save_event_url, data={
                'calendar': self.calendar.pk,
                'title': 'Episode 9',
                'desc': 'Silence of slums',
                'all_day': True,
                'start': '2016-12-13 15:19',
                'end': '2016-12-13 16:13',
                'timezone': '374',
                'attending_status': '1',
        })
        self.assertEqual(Event.objects.count(), 1)
        event = Event.objects.first()
        self.assertEqual(event.title, 'Episode 9')
        guest = Guest.objects.first()
        self.assertEqual(guest.attending_status, 1)

    def test_redirects_after_saving_event(self):
        response = self.client.post(
            self.save_event_url, data={
                'calendar': self.calendar.pk,
                'title': 'Episode 9',
                'desc': 'Silence of slums',
                'all_day': True,
                'start': '2016-12-13 15:19',
                'end': '2016-12-13 16:13',
                'timezone': '374',
                'attending_status': '1',
        })
        event = Event.objects.first()
        self.assertRedirects(response, '/event/{}'.format(event.pk))

    def test_saves_correct_date_and_hour(self):
        response = self.client.post(
            self.save_event_url, data={
                'calendar': self.calendar.pk,
                'title': 'Episode 9',
                'desc': 'Silence of slums',
                'all_day': False,
                'start': '2016-12-13 15:19',
                'end': '2016-12-13 16:13',
                'timezone': '374',
                'attending_status': '1',
            }, follow=True)
        europe = pytz.timezone('Europe/Warsaw')
        utc = pytz.timezone('UTC')
        start = datetime.datetime(2016, 12, 13, 15, 19)
        start = europe.localize(start).astimezone(utc)
        end = datetime.datetime(2016, 12, 13, 16, 13)
        end = europe.localize(end).astimezone(utc)
        event = Event.objects.first()
        self.assertContains(response, '15:19')
        self.assertEqual(event.start, start)
        self.assertContains(response, '16:13')
        self.assertEqual(event.end, end)

    def test_cannot_save_event_with_empty_title_or_dates(self):
        response = self.client.post(
            self.save_event_url, data={
                'calendar': self.calendar.pk,
                'title': '',
                'desc': 'Silence of slums',
                'all_day': True,
                'start': '',
                'end': '',
                'timezone': '374',
                'attending_status': '1',
        })
        self.assertEqual(Event.objects.count(), 0)
        self.assertIn('title', response.context['event_form'].errors)
        self.assertIn('start', response.context['event_form'].errors)
        self.assertIn('end', response.context['event_form'].errors)

    def test_passes_correct_initial_timezone_and_datetime(self):
        response = self.client.get(self.url)
        form = response.context['event_form']
        user_timezone = self.profile.get_timezone_display()
        start = self.start.astimezone(pytz.timezone(user_timezone))
        end = self.end.astimezone(pytz.timezone(user_timezone))
        self.assertAlmostEqual(form.initial['start'], start,
            delta=datetime.timedelta(seconds=1))
        self.assertAlmostEqual(form.initial['end'], end,
            delta=datetime.timedelta(seconds=1))
        event = Event(timezone=form.initial['timezone'])
        self.assertEqual(user_timezone, event.get_timezone_display())

    def test_others_cannot_save_event(self):
        amount = Event.objects.count()
        response = self.client.get('/logout')
        self.user_registers(username="Other")
        response = self.client.post(
            self.save_event_url, data={
                'calendar': self.calendar.pk,
                'title': 'Episode 9',
                'desc': 'Silence of slums',
                'all_day': True,
                'start': '2016-12-13 15:19',
                'end': '2016-12-13 16:13',
                'timezone': '374',
                'attending_status': '1',
        })
        self.assertEqual(amount, Event.objects.count())
        if amount:
            event = Event.objects.first()
            self.assertEqual(event.title, 'Radio Gaga')
            self.assertIn('access_denied', response.context)
        not_owner_profile = UserProfile.objects.get(user=get_user(self.client))
        # users that can read others calendars_amount
        # also shouldn't have access to modifications of events
        self.calendar.readers.add(not_owner_profile)
        response = self.client.post(
            self.save_event_url, data={
                'calendar': self.calendar.pk,
                'title': 'Episode 9',
                'desc': 'Silence of slums',
                'all_day': True,
                'start': '2016-12-13 15:19',
                'end': '2016-12-13 16:13',
                'timezone': '374',
                'attending_status': '1',
        })
        self.assertEqual(amount, Event.objects.count())
        if amount:
            event = Event.objects.first()
            self.assertEqual(event.title, 'Radio Gaga')
            self.assertIn('access_denied', response.context)
        else:
            self.assertIn('calendar', response.context['event_form'].errors)

    def test_user_with_modify_can_save_event(self):
        response = self.client.get('/logout')
        self.user_registers(username="Other")
        profile = UserProfile.objects.get(user=get_user(self.client))
        self.calendar.modifiers.add(profile)
        response = self.client.post(
            self.save_event_url, data={
                'calendar': self.calendar.pk,
                'title': 'Episode 9',
                'desc': 'Silence of slums',
                'all_day': True,
                'start': '2016-12-13 15:19',
                'end': '2016-12-13 16:13',
                'timezone': '374',
                'attending_status': '1',
        })
        self.assertEqual(Event.objects.count(), 1)
        event = Event.objects.first()
        self.assertEqual(event.title, 'Episode 9')



class EventViewTest(NewEventViewTest):

    def setUp(self):
        self.user_registers()
        profile = UserProfile.objects.get(user=get_user(self.client))
        self.calendar = MyCalendar.objects.create(owner=profile,
            name="Cindirella", color="E81AD4")
        self.calendar.readers.add(self.calendar.owner)
        self.calendar.modifiers.add(self.calendar.owner)
        self.start = pytz.utc.localize(datetime.datetime.utcnow())
        self.end = self.start + datetime.timedelta(minutes=30)
        self.event = Event.objects.create(calendar=self.calendar,
            title='Radio Gaga', desc='Radio Blabla',
            timezone=374, start=self.start, end=self.end, all_day=True)
        self.guest = Guest.objects.create(event=self.event, user=profile,
            attending_status=Guest.MAYBE)
        self.url = '/event/1'
        self.save_event_url = '/edit_event/1'
        self.add_guest_url = '/add_guest/1'
        self.rsvp_url = '/rsvp_to_event/1'
        self.template = 'my_calendar/event.html'
        self.function = event_view

    def test_saves_event(self):
        self.client.post(
            self.save_event_url, data={
                'calendar': self.calendar.pk,
                'title': 'Episode 9',
                'desc': 'Silence of slums',
                'all_day': True,
                'start': '2016-12-13 15:19',
                'end': '2016-12-13 16:13',
                'timezone': '374',
                'attending_status': '1',
        })
        self.assertEqual(Event.objects.count(), 1)
        event = Event.objects.first()
        self.assertEqual(event.title, 'Episode 9')
        guest = Guest.objects.first()
        self.assertNotEqual(guest.attending_status, 1)

    def test_cannot_save_event_with_empty_title_or_dates(self):
        title = Event.objects.first().title
        response = self.client.post(
            self.save_event_url, data={
                'calendar': self.calendar.pk,
                'title': '',
                'desc': '',
                'all_day': True,
                'start': '',
                'end': '',
                'timezone': '374',
                'attending_status': '1',
        }, follow=True)
        event = Event.objects.first()
        self.assertEqual(event.title, title)
        self.assertEqual(Event.objects.count(), 1)
        self.assertIn('title', response.context['form_errors'])
        self.assertIn('start', response.context['form_errors'])
        self.assertIn('end', response.context['form_errors'])

    def test_passes_correct_initial_timezone_and_datetime(self):
        response = self.client.get(self.url)
        form = response.context['event_form']
        timezone = pytz.timezone(self.event.get_timezone_display())
        start = self.start.astimezone(timezone)
        end = self.end.astimezone(timezone)
        self.assertAlmostEqual(form.initial['start'], start,
            delta=datetime.timedelta(seconds=1))
        self.assertAlmostEqual(form.initial['end'], end,
            delta=datetime.timedelta(seconds=1))
        self.assertEqual(self.event.timezone, form.initial['timezone'])

    def test_saves_guest(self):
        self.client.get('/logout')
        self.user_registers(username="Human")
        self.client.get('/logout')
        self.client.post(
            '/login', data={
            'username': 'John123',
            'password': 'password'
            })
        self.client.post(self.add_guest_url, data={
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
        response = self.client.post(self.add_guest_url, data={
            'user': 1,
        }, follow=True)
        self.assertEqual(Guest.objects.count(), 1)
        self.assertEqual(response.context['form_errors']['user'],
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

    def test_guest_can_see_event(self):
        self.client.get('/logout')
        self.user_registers(username="Human")
        profile = UserProfile.objects.get(user=get_user(self.client))
        Guest.objects.create(user=profile, event=self.event)

        response = self.client.get(self.url)
        self.assertIn('event', response.context)
        self.assertIn('guests', response.context)
        self.assertIn('user_is_guest', response.context)
        self.assertIn('attending_status_form', response.context)

    def test_saves_attending_status(self):
        response = self.client.post(
            self.rsvp_url, data={
                'attending_status': '1',
        })
        self.assertEqual(Guest.objects.first().attending_status, 1)

        self.client.get('/logout')
        self.user_registers(username="Human")
        profile = UserProfile.objects.get(user=get_user(self.client))
        Guest.objects.create(user=profile, event=self.event)

        response = self.client.post(
            self.rsvp_url, data={
                'attending_status': '4',
        })
        guest = Guest.objects.get(user=profile, event=self.event)
        self.assertEqual(guest.attending_status, 4)



if __name__ == '__main__':
    unittest.main()
