import datetime
import pytz

from django.contrib.auth import get_user

from my_calendar.views import month, week, day
from my_calendar.models import (UserProfile, MyCalendar, Event, Guest)
from .test_views_base import BaseViewTest


class DayViewTest(BaseViewTest):

    def setUp(self):
        self.user_registers()
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
        profile = UserProfile.objects.get(user=get_user(self.client))
        calendar_ = MyCalendar.objects.create(owner=profile, color="#000FFF")
        start = datetime.datetime.combine(self.today, datetime.time(13, 30))
        start = pytz.utc.localize(start)
        end = start + datetime.timedelta(minutes=30)
        event = Event.objects.create(calendar=calendar_,
            start=start, end=end, all_day=False)
        guest = Guest.objects.create(event=event, user=profile)
        response = self.client.get(self.url)
        for dict_ in response.context['days']:
            if dict_['day'] == self.today:
                dict_ = dict_['events'][0]
                break
        self.assertEqual(event.pk, dict_['pk'])
        self.assertEqual(event.title, dict_['title'])
        self.assertEqual(event.start, dict_['start'])
        self.assertEqual(event.end, dict_['end'])
        self.assertEqual(event.all_day, dict_['all_day'])
        height = (end - start).total_seconds() / (24 * 60 * 60)
        # timezone of timeline is a timezone of the user, not event
        europe = pytz.timezone(profile.get_timezone_display())
        beginning = datetime.datetime.combine(self.today, datetime.time(0))
        beginning = europe.localize(beginning)
        top = (start - beginning).total_seconds() / (24 * 60 * 60)
        self.assertEqual(height, dict_['height'])
        self.assertEqual(top, dict_['top'])
        self.assertEqual(calendar_.color, dict_['color'])
        self.assertEqual(calendar_.pk, dict_['class'])

    def test_event_height_when_time_change(self):
        profile = UserProfile.objects.get(user=get_user(self.client))
        calendar_ = MyCalendar.objects.create(owner=profile, color="#000FFF")
        europe = pytz.timezone(profile.get_timezone_display())
        time_change = datetime.date(2016, 10, 30)
        start = datetime.datetime.combine(time_change, datetime.time(0, 0))
        start = europe.localize(start)
        end = datetime.datetime.combine(time_change, datetime.time(4, 0))
        end = europe.localize(end)
        event = Event.objects.create(calendar=calendar_,
            start=start, end=end, all_day=False)
        guest = Guest.objects.create(event=event, user=profile)
        response = self.client.get(self.base_url + '/2016-10-30')
        for dict_ in response.context['days']:
            if dict_['day'] == time_change:
                dict_ = dict_['events'][0]
                break
        height = (4 * 3600) / (24 * 60 * 60)
        self.assertEqual(height, dict_['height'])

    def test_passes_correct_earlier_and_later(self):
        response = self.client.get(self.url)
        earlier = self.today - datetime.timedelta(days=1)
        self.assertEqual(response.context['earlier'], earlier)
        later = self.today + datetime.timedelta(days=1)
        self.assertEqual(response.context['later'], later)

class MonthViewTest(DayViewTest):

    def setUp(self):
        self.user_registers()
        self.today = datetime.datetime.now().date()
        self.base_url = '/month'
        self.date_url()
        self.template = 'my_calendar/month.html'
        self.function = month

    def get_days_from_context(self, context):
        days = set()
        for day_dict in context['days']:
            days.add(day_dict['day'])
        return days

    def passes_days_if_date_is_today(self, response):
        first = datetime.date(self.today.year, self.today.month, 1)
        some = datetime.date(self.today.year, self.today.month, 25)
        days = self.get_days_from_context(response.context)
        self.assertIn(first, days)
        self.assertIn(some, days)

    def test_passes_days_of_month_in_context(self):
        response = self.client.get(self.url)
        self.passes_days_if_date_is_today(response)

    def test_passes_correct_days_when_month_given(self):
        response = self.client.get(self.base_url + '/2015-02-01')
        first = datetime.date(2015, 1, 26)
        last = datetime.date(2015, 3, 1)
        days = self.get_days_from_context(response.context)
        self.assertIn(first, days)
        self.assertIn(last, days)
        self.assertEqual(len(days), 35)

    def test_passes_correct_earlier_and_later(self):
        response = self.client.get(self.base_url + '/2016-01-12')
        earlier = datetime.date(year=2015, month=12, day=1)
        self.assertEqual(response.context['earlier'], earlier)
        later = datetime.date(year=2016, month=2, day=1)
        self.assertEqual(response.context['later'], later)

class WeekViewTest(DayViewTest):

    def setUp(self):
        self.user_registers()
        self.today = datetime.datetime.now().date()
        self.base_url = '/week'
        self.date_url()
        self.template = 'my_calendar/week.html'
        self.function = week

    def get_days_from_context(self, context):
        days = set()
        for day_dict in context['days']:
            days.add(day_dict['day'])
        return days

    def passes_days_if_date_is_today(self, response):
        yesterday = self.today - datetime.timedelta(days=1)
        tommorow = self.today + datetime.timedelta(days=1)
        days = self.get_days_from_context(response.context)
        self.assertTrue(yesterday in days or tommorow in days)

    def test_passes_days_of_week_in_context(self):
        response = self.client.get(self.url)
        self.passes_days_if_date_is_today(response)

    def test_passes_correct_days_when_week_given(self):
        response = self.client.get(self.base_url + '/2015-02-01')
        first = datetime.date(2015, 1, 26)
        last = datetime.date(2015, 2, 1)
        days = self.get_days_from_context(response.context)
        self.assertIn(first, days)
        self.assertIn(last, days)
        self.assertEqual(len(days), 7)

    def test_passes_correct_earlier_and_later(self):
        response = self.client.get(self.url)
        earlier = self.today - datetime.timedelta(days=7)
        self.assertEqual(response.context['earlier'], earlier)
        later = self.today + datetime.timedelta(days=7)
        self.assertEqual(response.context['later'], later)


if __name__ == '__main__':
    unittest.main()
