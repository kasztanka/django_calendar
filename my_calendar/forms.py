from pytz import common_timezones_set

from django.contrib.auth.models import User
from django import forms

from .models import EventCustomSettings, Guest

TIMEZONES = list(common_timezones_set)
TIMEZONES.sort()
TIMEZONES = ((str(i + 1), tz) for i, tz in enumerate(TIMEZONES))

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')

class EventForm(forms.ModelForm):
    start_date = forms.DateField(label="From", input_formats=['%m/%d/%Y'],
        widget=forms.DateInput(attrs={'class': 'datepicker'}))
    start_hour = forms.TimeField(label="", input_formats=['%H:%M'],
        widget=forms.TimeInput(attrs={'class': 'time'}))
    end_date = forms.DateField(label="To", input_formats=['%m/%d/%Y'],
        widget=forms.DateInput(attrs={'class': 'datepicker'}))
    end_hour = forms.TimeField(label="", input_formats=['%H:%M'],
        widget=forms.TimeInput(attrs={'class': 'time'}))
    
    class Meta:
        model = EventCustomSettings
        fields = ('title', 'desc', 'all_day', 'timezone')
        widgets = {
            'timezone': forms.Select(choices=TIMEZONES)
        }
        labels = {
            'desc': 'Description',
        }
        
        
class StateForm(forms.ModelForm):
    
    class Meta:
        model = Guest
        fields = ('state',)