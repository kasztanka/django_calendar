from pytz import common_timezones_set

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
    TIMEZONES = ((i + 1, tz) for i, tz in enumerate(TIMEZONES))
    # 436 is UTC
    timezone = models.IntegerField(choices=TIMEZONES, default=436)

    def get_own_calendars(self):
        """
        Returns a queryset of usere's own calendars.
        """
        return MyCalendar.objects.filter(owner=self)

    def get_calendars_to_modify(self):
        """
        Returns a queryset of calendars that user can modify
        but doesn't own.
        """
        return MyCalendar.objects.filter(modifiers=self)

    def get_calendars_to_read(self):
        """
        Returns a queryset of calendars that user can read
        but dooesn't own.
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

    def __str__(self):
        return self.user.username + ", timezone: " + self.get_timezone_display()


class MyCalendarManager(models.Manager):
    """
    When calendar is created, owner should be added
    to modifiers and readers fields.
    """
    def create(self, *args, **kwargs):
        calendar_ = super(MyCalendarManager, self).create(*args, **kwargs)
        calendar_.readers.add(calendar_.owner)
        calendar_.modifiers.add(calendar_.owner)
        return calendar_


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
    color = models.CharField(max_length=6) # default = #464AFF?
    modifiers = models.ManyToManyField(
        UserProfile, related_name='calendars_to_modify', blank=True)
    readers = models.ManyToManyField(
        UserProfile, related_name='calendars_to_read', blank=True)
    objects = MyCalendarManager()

    def __str__(self):
        return self.name

class Event(models.Model):
    """
    Event belongs to single calendar.
    Other users can be invited to it - they become guests.
    User who creates event should automatically be guest.
    """
    calendar = models.ForeignKey(MyCalendar, on_delete=models.CASCADE)

    def get_owner_settings(self):
        """
        Method can be used to get owner's settings.
        """
        guest = Guest.objects.filter(
            event=self
        ).get(
            user=self.calendar.owner
        )
        return EventCustomSettings.objects.get(guest=guest)


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

    def get_settings(self):
        """
        Method can be used to get guest's custom settings.
        If he doesn't have any, method returns settings of the owner.
        Also it returns the info which settings are returned.
        """
        settings_belong_to_owner = False
        try:
            settings = EventCustomSettings.objects.get(guest=self)
        except EventCustomSettings.DoesNotExist:
            settings = self.event.get_owner_settings()
            settings_belong_to_owner = True
        return settings, settings_belong_to_owner


class EventCustomSettings(models.Model):
    """
    Every guest can edit settings of the event:
    title, description, timezone, date, time
    and duration of event (all day or specific hours).
    Default settings are chosen by owner.
    Once user changes some settings, he won't be able to see
    the changes made by the owner of the event.
    """
    guest = models.OneToOneField(Guest, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    desc = models.CharField(max_length=1000, default="", blank=True)
    TIMEZONES = list(common_timezones_set)
    TIMEZONES.sort()
    TIMEZONES = ((i + 1, tz) for i, tz in enumerate(TIMEZONES))
    # 436 is UTC
    timezone = models.IntegerField(choices=TIMEZONES, default=436)
    start = models.DateTimeField()
    end = models.DateTimeField()
    all_day = models.BooleanField()
