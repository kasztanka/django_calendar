from django.contrib import admin

from .models import UserProfile, MyCalendar, Event, Guest


for model in (UserProfile, MyCalendar, Event, Guest):
    admin.site.register(model)
