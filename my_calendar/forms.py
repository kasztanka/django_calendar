import datetime
import pytz

from django.core.exceptions import ValidationError
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
        fields = ('readers', 'modifiers')
        widgets = {
            'readers': forms.CheckboxSelectMultiple,
            'modifiers': forms.CheckboxSelectMultiple,
        }

    def __init__(self, owner=None, *args, **kwargs):
        """
        Removes owner from selections for modifiers and readers.
        """
        super(CalendarForm, self).__init__(*args, **kwargs)
        if owner is not None:
            without_owner = UserProfile.objects.all().exclude(pk=owner.pk)
            self.fields['readers'].queryset = without_owner
            self.fields['modifiers'].queryset = without_owner


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
        instance = kwargs.get('instance', None)
        if instance != None:
            start = instance.start
            end = instance.end
        timezone = kwargs.pop('timezone', None)
        if instance != None and timezone != None:
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


class AttendingStatusForm(forms.ModelForm):

    class Meta:
        model = Guest
        fields = ('attending_status',)


class GuestForm(forms.ModelForm):

    class Meta:
        model = Guest
        fields = ('user',)

    def __init__(self, event, *args, **kwargs):
        super(GuestForm, self).__init__(*args, **kwargs)
        self.instance.event = event

    def validate_unique(self):
        try:
            self.instance.validate_unique()
        except ValidationError as e:
            e.error_dict = {'user': [("This user is already guest added to "
            + "this event.")]}
            self._update_errors(e)
