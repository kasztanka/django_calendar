import datetime
import pytz

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase


from my_calendar.models import (UserProfile, MyCalendar, Event, Guest)


class UserProfileTest(TestCase):

    def test_default_timezone_utc(self):
        user = User.objects.create(username='John')
        profile = UserProfile.objects.create(user=user)
        TIMEZONES = list(pytz.common_timezones_set)
        TIMEZONES.sort()
        TIMEZONES = tuple((i + 1, tz) for i, tz in enumerate(TIMEZONES))
        UTC_index = next(x[0] for x in reversed(TIMEZONES) if x[1] == 'UTC')
        self.assertEqual(profile.timezone, UTC_index)
        self.assertEqual(profile.get_timezone_display(), 'UTC')


class MyCalendarTest(TestCase):

    def test_owner_added_to_readers_during_creation(self):
        user_ = User.objects.create(username="Owner")
        profile = UserProfile.objects.create(user=user_)
        calendar_ = MyCalendar.objects.create(owner=profile,
            name="Cindirella", color="E81AD4")
        self.assertIn(profile, calendar_.readers.all())
        self.assertEqual(len(calendar_.readers.all()), 1)

    def test_owner_added_to_modifiers_during_creation(self):
        user_ = User.objects.create(username="Owner")
        profile = UserProfile.objects.create(user=user_)
        calendar_ = MyCalendar.objects.create(owner=profile,
            name="Cindirella", color="E81AD4")
        self.assertIn(profile, calendar_.modifiers.all())
        self.assertEqual(len(calendar_.modifiers.all()), 1)

    def test_no_duplicates_in_readers_and_modifiers(self):
        user_ = User.objects.create(username="Owner")
        profile = UserProfile.objects.create(user=user_)
        calendar_ = MyCalendar.objects.create(owner=profile,
            name="Cindirella", color="E81AD4")

        calendar_.readers.add(profile)
        self.assertEqual(len(calendar_.readers.all()), 1)

        calendar_.modifiers.add(profile)
        self.assertEqual(len(calendar_.modifiers.all()), 1)


class GuestTest(TestCase):

    def test_duplicates_invalid(self):
        user = User.objects.create(username="Owner")
        profile = UserProfile.objects.create(user=user)
        calendar = MyCalendar.objects.create(owner=profile,
            name="Cindirella", color="E81AD4")
        start = pytz.utc.localize(datetime.datetime.now())
        end = start + datetime.timedelta(minutes=30)
        event = Event.objects.create(calendar=calendar, start=start, end=end,
            title="Some title", all_day=True)
        Guest.objects.create(event=event, user=profile)
        with self.assertRaises(ValidationError):
            guest = Guest(event=event, user=profile)
            guest.full_clean()


class EventTest(TestCase):

    def test_default_timezone_utc(self):
        event = Event()
        self.assertEqual(event.get_timezone_display(), str(pytz.utc))


if __name__ == '__main__':
    unittest.main()
