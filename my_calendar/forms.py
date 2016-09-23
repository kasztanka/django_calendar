import datetime
import pytz

from django.contrib.auth.models import User
from django import forms

from .models import EventCustomSettings, Guest, UserProfile, MyCalendar


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')
        
        
class ProfileForm(forms.ModelForm):
    
    class Meta:
        model = UserProfile
        fields = ('timezone',)
        error_messages = {
            'timezone': {'invalid_choice': "Wrong timezone was chosen."}
        }
        
        
class CalendarForm(forms.ModelForm):
    
    class Meta:
        model = MyCalendar
        fields = ('can_read', 'can_modify')
        widgets = {
            'can_read': forms.CheckboxSelectMultiple,
            'can_modify': forms.CheckboxSelectMultiple,
        }
        

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
        error_messages = {
            'timezone': {'invalid_choice': "Wrong timezone was chosen."}
        }
        labels = {
            'desc': 'Description',
        }
        
    def __init__(self, *args, **kwargs):
        start = kwargs.pop('start', None)
        end = kwargs.pop('end', None)
        timezone = kwargs.pop('timezone', None)
        if start != None and end != None and timezone != None:
            start = start.astimezone(timezone['tz'])
            end = end.astimezone(timezone['tz'])
            kwargs.update(initial={
                'start_date': start.strftime('%m/%d/%Y'),
                'start_hour': start.strftime('%H:%M'),
                'end_date': end.strftime('%m/%d/%Y'),
                'end_hour': end.strftime('%H:%M'),
                'timezone': timezone['number'],
            })
        super(EventForm, self).__init__(*args, **kwargs)        
        
    def is_valid(self):
        valid = super(EventForm, self).is_valid()
        if not valid:
            return valid
        
        start = datetime.datetime.strptime(self.data['start_date']
            + ' ' + self.data['start_hour'], '%m/%d/%Y %H:%M')
        end = datetime.datetime.strptime(self.data['end_date']
            + ' ' + self.data['end_hour'], '%m/%d/%Y %H:%M')
        
        if self.data.get('all_day', False):
            if start.date() > end.date():
                self._errors['end_date'] = ['The event must end after its beginning.']
                return False
        elif start > end:
            self._errors['end_date'] = ['The event must end after its beginning.']
            return False
        return True
    
    def save(self, commit=True):
        instance = super(EventForm, self).save(commit=False)
        tz = pytz.timezone(instance.get_timezone_display())
        start = datetime.datetime.strptime(self.data['start_date']
            + ' ' + self.data['start_hour'], '%m/%d/%Y %H:%M')
        instance.start = tz.localize(start).astimezone(pytz.utc)
        end = datetime.datetime.strptime(self.data['end_date']
            + ' ' + self.data['end_hour'], '%m/%d/%Y %H:%M')
        instance.end = tz.localize(end).astimezone(pytz.utc)
        
        if commit:
            instance.save()
        return instance
        
        
class StateForm(forms.ModelForm):
    
    class Meta:
        model = Guest
        fields = ('state',)