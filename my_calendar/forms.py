import datetime
import pytz

from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django import forms

from .models import Event, Guest, UserProfile, MyCalendar

WRONG_TIMEZONE_ERROR = "Wrong timezone was chosen."
END_BEFORE_START_ERROR = "The event must end after its beginning."
NO_ACCESS_TO_CALENDAR = "You have no access to this calendar."
DUPLICATE_GUEST_ERROR = "This user is already guest added to this event."
WRONG_ATTENDING_STATUS_ERROR = "Wrong attending status was chosen."


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
            'timezone': {'invalid_choice': WRONG_TIMEZONE_ERROR}
        }


class CalendarForm(forms.ModelForm):

    class Meta:
        model = MyCalendar
        fields = ('name', 'color', 'readers', 'modifiers')
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
            self.owner = owner
            without_owner = UserProfile.objects.all().exclude(pk=owner.pk)
            self.fields['readers'].queryset = without_owner
            self.fields['modifiers'].queryset = without_owner

    def save(self, commit=True):
        instance = super(CalendarForm, self).save(commit=False)
        instance.owner = self.owner
        if commit:
            instance.save()
            instance.readers = self.cleaned_data['readers']
            instance.readers.add(instance.owner)
            instance.modifiers = self.cleaned_data['modifiers']
            instance.modifiers.add(instance.owner)
        return instance


class EventForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = ('calendar', 'start', 'end', 'title', 'desc', 'all_day', 'timezone')
        error_messages = {
            'timezone': {'invalid_choice': WRONG_TIMEZONE_ERROR}
        }

    def __init__(self, user, *args, **kwargs):
        instance = kwargs.get('instance', None)
        timezone = kwargs.pop('timezone', None)
        if instance is not None and timezone is not None:
            kwargs.update(initial={
                'start': instance.start.astimezone(timezone['tz']),
                'end': instance.end.astimezone(timezone['tz']),
                'timezone': timezone['number'],
            })
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['calendar'].queryset = user.get_calendars_to_modify()
        self.fields['calendar'].empty_label = 'Select calendar'

    def is_valid(self, user):
        valid = super(EventForm, self).is_valid()

        start = self.cleaned_data['start']
        end = self.cleaned_data['end']
        if self.cleaned_data['all_day']:
            if start.date() > end.date():
                self.add_error('end', END_BEFORE_START_ERROR)
                valid = False
        elif start > end:
            self.add_error('end', END_BEFORE_START_ERROR)
            valid = False

        if user not in self.cleaned_data['calendar'].modifiers.all():
            self.add_error('calendar', NO_ACCESS_TO_CALENDAR)
            valid = False
        return valid

    def save(self, commit=True):
        instance = super(EventForm, self).save(commit=False)
        tz = pytz.timezone(instance.get_timezone_display())
        start = self.cleaned_data['start'].replace(tzinfo=None)
        instance.start = tz.localize(start).astimezone(pytz.utc)
        end = self.cleaned_data['end'].replace(tzinfo=None)
        instance.end = tz.localize(end).astimezone(pytz.utc)

        if commit:
            instance.save()
        return instance


class AttendingStatusForm(forms.ModelForm):

    class Meta:
        model = Guest
        fields = ('attending_status',)
        error_messages = {
            'attending_status': {'invalid_choice': WRONG_ATTENDING_STATUS_ERROR}
        }


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
            self.add_error('user', DUPLICATE_GUEST_ERROR)
