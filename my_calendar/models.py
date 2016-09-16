from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """
    Extension of the User class.
    Added timezone.
    """
    user = models.OneToOneField(User)
    timezone = models.CharField(max_length=50)
    
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
        return MyCalendar.objects.filter(can_modify=self)
    
    def get_calendars_to_read(self):
        """
        Returns a queryset of calendars that user can read
        but dooesn't own.
        """
        return MyCalendar.objects.filter(can_read=self)
    
    def get_events(self):
        """
        Returns events where user is guest at.
        """
        events = []
        guests = Guest.objects.filter(user=self)
        for guest in guests:
            events.append(guest.event)
        return events
    
    def get_not_owned_events(self):
        """
        Returns events where user is guest at but which he doesn't own.
        """
        events = []
        guests = Guest.objects.filter(user=self)
        for guest in guests:
            if guest.user != guest.event.calendar.owner:
                events.append(guest.event)
        return events
        
    def __str__(self):
        return self.user.username + ", timezone: " + self.timezone


class MyCalendar(models.Model):
    """
    Model of the calendar.
    Calendar belongs to single user.
    Attributes: owner, name, color, can_modify, can_read.
    Last two contains users who can modify/read a calendar.
    """
    owner = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE,
        related_name='owned_calendars')
    name = models.CharField(max_length=100, default="")
    color = models.CharField(max_length=6) # default = #464AFF?
    can_modify = models.ManyToManyField(
        UserProfile, related_name='calendars_to_modify')
    can_read = models.ManyToManyField(
        UserProfile, related_name='calendars_to_read')
    
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
    by choosing one of the four states:
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
    STATE_CHOICES = (
        (GOING, "Going"),
        (MAYBE, "Maybe"),
        (UNKNOWN, "Unknown"),
        (NOT_GOING, "Not going"),
    )
    state = models.IntegerField(choices=STATE_CHOICES, default=UNKNOWN)
    
    def get_settings(self):
        """
        Method can be used to get guest's custom settings.
        If he doesn't have any, method returns settings of the owner.
        """
        settings = EventCustomSettings.objects.get(guest=self)
        if settings == None:
            settings = self.event.get_owner_settings()
        return settings


class EventCustomSettings(models.Model):
    """
    Every guest can edit settings of the event:
    title, description, timezone, date, time
    and duration of event (all day or specific hours).
    Default settings are chosen by owner.
    Once user changes some settings, he won't be able to see
    the changes made by the owner of the event.
    """
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    desc = models.CharField(max_length=1000, default="", blank=True)
    timezone = models.CharField(max_length=50)
    start = models.DateTimeField()
    end = models.DateTimeField()
    all_day = models.BooleanField()