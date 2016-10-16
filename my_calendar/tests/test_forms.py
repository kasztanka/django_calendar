import datetime
import pytz

from django.contrib.auth.models import User
from django.test import TestCase

from my_calendar.models import (UserProfile, MyCalendar, Event, Guest,
    EventCustomSettings)
from my_calendar.forms import (
    RegisterForm, EventForm, GuestForm, ProfileForm, CalendarForm,
    AttendingStatusForm,
    WRONG_TIMEZONE_ERROR, END_BEFORE_START_ERROR, DUPLICATE_GUEST_ERROR,
    WRONG_ATTENDING_STATUS_ERROR,
)


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
        form = RegisterForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn(
            "This field is required.",
            form.errors['username']
        )
        self.assertIn(
            "This field is required.",
            form.errors['password']
        )


class ProfileFormTest(TestCase):

    def test_valid_data(self):
        form = ProfileForm(data={'timezone': '1'})
        self.assertTrue(form.is_valid())

    def test_wrong_data(self):
        # empty data
        form = ProfileForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("This field is required.", form.errors['timezone'])
        # not valid timezone
        tz_len = len(pytz.common_timezones_set)
        form = ProfileForm(data={'timezone': str(tz_len + 10)})
        self.assertFalse(form.is_valid())
        self.assertIn(WRONG_TIMEZONE_ERROR, form.errors['timezone'])


class CalendarFormTest(TestCase):

    def test_blank_data_ok(self):
        form = CalendarForm(data={})
        self.assertTrue(form.is_valid())

    def test_owner_is_not_choice_for_modifiers_or_readers_when_given(self):
        profiles = []
        for i in range(3):
            user = User.objects.create(username='user{}'.format(i))
            profiles.append(UserProfile.objects.create(user=user))
        form = CalendarForm(owner=profiles[0])
        without_owner = [profiles[1], profiles[2]]
        self.assertEqual(list(form.fields['readers'].queryset), without_owner)
        self.assertEqual(list(form.fields['modifiers'].queryset), without_owner)


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

    def test_blank_data(self):
        form = EventForm(data={})
        self.assertFalse(form.is_valid())
        fields = ['title', 'start_hour', 'start_date', 'end_hour', 'end_date',
            'timezone']
        for field in fields:
            self.assertIn(
                "This field is required.",
                form.errors[field]
            )

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
        self.assertIn(END_BEFORE_START_ERROR, form.errors['end_date'])

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
        self.assertIn(END_BEFORE_START_ERROR, form.errors['end_date'])

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
        self.assertIn(WRONG_TIMEZONE_ERROR, form.errors['timezone'])


class GuestFormTest(TestCase):

    def setUp(self):
        user_ = User.objects.create(username="Owner")
        self.profile = UserProfile.objects.create(user=user_)
        calendar = MyCalendar.objects.create(owner=self.profile,
            name="Cindirella", color="E81AD4")
        self.event = Event.objects.create(calendar=calendar)

    def test_valid_data(self):
        form = GuestForm(event=self.event, data={'user': 1})
        self.assertTrue(form.is_valid())

    def test_wrong_data(self):
        # not existing user
        form = GuestForm(event=self.event, data={'user': 2})
        self.assertFalse(form.is_valid())
        # empty data
        form = GuestForm(event=self.event, data={})
        self.assertFalse(form.is_valid())

    def test_form_validates_duplicate_guests(self):
        Guest.objects.create(event=self.event, user=self.profile)
        form = GuestForm(event=self.event, data={'user': 1})
        self.assertFalse(form.is_valid())
        self.assertIn(DUPLICATE_GUEST_ERROR, form.errors['user'])

    def test_no_event_raise_error(self):
        with self.assertRaises(TypeError):
            form = GuestForm(data={'user': 1})

    def test_saves_guest_correctly(self):
        form = GuestForm(event=self.event, data={'user': 1})
        form.save()
        guest = Guest.objects.first()
        self.assertEqual(guest.event, self.event)
        self.assertEqual(guest.user, self.profile)


class AttendingStatusFormTest(TestCase):

    def test_valid_data(self):
        form = AttendingStatusForm(data={'attending_status': '1'})
        self.assertTrue(form.is_valid())

    def test_wrong_data(self):
        # empty data
        form = AttendingStatusForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn(
            "This field is required.",
            form.errors['attending_status']
        )
        # not valid attending status
        form = AttendingStatusForm(data={'attending_status': '6'})
        self.assertFalse(form.is_valid())
        self.assertIn(
            WRONG_ATTENDING_STATUS_ERROR,
            form.errors['attending_status']
        )



if __name__ == '__main__':
    unittest.main()
