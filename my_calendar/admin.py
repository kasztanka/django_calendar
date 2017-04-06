from django.contrib import admin

from .models import UserProfile, MyCalendar, Event, Guest


admin.site.register((UserProfile, MyCalendar, Event, Guest))
