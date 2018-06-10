from pytz import common_timezones_set
import datetime
import re

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """
    Extension of the User class.
    Added timezone.
    """
    user = models.OneToOneField(User)
    TIMEZONES = list(common_timezones_set)
    TIMEZONES.sort()
    TIMEZONES = tuple((i + 1, tz) for i, tz in enumerate(TIMEZONES))
    UTC_index = next(x[0] for x in reversed(TIMEZONES) if x[1] == 'UTC')
    timezone = models.IntegerField(choices=TIMEZONES, default=UTC_index)

    def get_own_calendars(self):
        """
        Returns a queryset of usere's own calendars.
        """
        return MyCalendar.objects.filter(owner=self)

    def get_calendars_to_modify(self):
        """
        Returns a queryset of calendars that user can modify.
        """
        return MyCalendar.objects.filter(modifiers=self)

    def get_calendars_to_read(self):
        """
        Returns a queryset of calendars that user can read.
        """
        return MyCalendar.objects.filter(readers=self)

    def get_all_events(self):
        """
        Returns events that user has access to.
        """
        events = set()
        for calendar in (self.get_calendars_to_modify()
            | self.get_calendars_to_read()):
            events_ = Event.objects.filter(calendar=calendar)
            for ev in events_:
                events.add(ev)
        guests = Guest.objects.filter(user=self)
        for guest in guests:
            events.add(guest.event)
        return events

    def get_upcoming_events(self, amount):
        all_events = self.get_all_events()
        upcoming_events = []
        for event in all_events:
            start = event.start.replace(tzinfo=None)
            if start >= datetime.datetime.now():
                upcoming_events.append(event)
        upcoming_events.sort(key=lambda x: x.start)
        return upcoming_events[-amount:]

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name

def validate_color(value):
    pattern = re.compile("^#[A-Fa-f0-9]{6}$")
    if not pattern.match(value):
        raise ValidationError(
            _('%(value)s is not color - hexadecimal with hash at the beginning'),
            params={'value': value},
        )

class MyCalendar(models.Model):
    """
    Model of the calendar.
    Calendar belongs to single user.
    Attributes: owner, name, color, modifiers, readers.
    """
    owner = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE,
        related_name='owned_calendars')
    name = models.CharField(max_length=100, default="")
    color = models.CharField(max_length=7, validators=[validate_color])
    modifiers = models.ManyToManyField(
        UserProfile, related_name='calendars_to_modify', blank=True)
    readers = models.ManyToManyField(
        UserProfile, related_name='calendars_to_read', blank=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    """
    Event belongs to single calendar.
    Other users can be invited to it - they become guests.
    User who creates event should automatically be guest.
    """
    calendar = models.ForeignKey(MyCalendar, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    desc = models.CharField(max_length=1000, default="", blank=True)

    TIMEZONES = list(common_timezones_set)
    TIMEZONES.sort()
    TIMEZONES = tuple((i + 1, tz) for i, tz in enumerate(TIMEZONES))
    UTC_index = next(x[0] for x in reversed(TIMEZONES) if x[1] == 'UTC')
    timezone = models.IntegerField(choices=TIMEZONES, default=UTC_index)

    start = models.DateTimeField()
    end = models.DateTimeField()
    all_day = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Guest(models.Model):
    """
    Owner of an event can invite other users to it.
    Guests (also owner) responds to an invitation
    by choosing one of the four options:
        -> Going
        -> Maybe
        -> Unknown
        -> Not going
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    GOING = 1
    MAYBE = 2
    UNKNOWN = 3
    NOT_GOING = 4
    ATTENDING_STATUS_CHOICES = (
        (GOING, "Going"),
        (MAYBE, "Maybe"),
        (UNKNOWN, "Unknown"),
        (NOT_GOING, "Not going"),
    )
    attending_status = models.IntegerField(choices=ATTENDING_STATUS_CHOICES, default=UNKNOWN)
    class Meta:
        unique_together = ('event', 'user')
        # unique_together changes default ordering e.g. for objects.all()
        ordering = ['id']
