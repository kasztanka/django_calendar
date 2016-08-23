from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    timezone = models.CharField(max_length=50)
    def get_calendars(self):
        # or maybe owned_calendars + calendars_to_modify + calendars_to_read
        calendars = MyCalendar.objects.filter(
            models.Q(owner=self) |
            models.Q(can_modify=self) |
            models.Q(can_read=self)
        )
        return calendars
    def get_events(self):
        events = []
        guests = Guest.objects.filter(user=self)
        for guest in guests:
            events.append(guest.event)
        return events
    def get_not_owned_events(self):
        events = []
        guests = Guest.objects.filter(user=self)
        for guest in guests:
            if guest.user != guest.event.calendar.owner:
                events.append(guest.event)
        return events
        
    def __str__(self):
        return self.user.username + ", timezone: " + timezone

class MyCalendar(models.Model):
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='owned_calendars')
    name = models.CharField(max_length=100, default="")
    color = models.CharField(max_length=6) # default = #464AFF?
    can_modify = models.ManyToManyField(UserProfile, related_name='calendars_to_modify')
    can_read = models.ManyToManyField(UserProfile, related_name='calendars_to_read')
    def __str__(self):
        return self.name

class Event(models.Model):
    calendar = models.ForeignKey(MyCalendar, on_delete=models.CASCADE)
    def get_owner_changes(self):
        return GuestChanges.object.filter(
            event=self
        ).filter(
            user=self.calendar.owner
        )

class Guest(models.Model):
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
    def get_changes(self):
        changes = GuestChanges.objects.get(guest=self)
        if changes == None:
            changes = self.event.get_default()
        return changes

class GuestChanges(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    desc = models.CharField(max_length=1000, default="")
    timezone = models.CharField(max_length=50)
    start = models.DateTimeField()
    end = models.DateTimeField()
    all_day = models.BooleanField()
    # save as utc!