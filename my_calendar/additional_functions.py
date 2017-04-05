from calendar import monthrange
import datetime
import pytz

from .models import Guest

COLORS = (
    "E81AD4",
    "8F00FF",
    "6214CC",
    "464AFF",
)

def fill_month(date_):
    '''
    Function that returns list of days of month for given date
    plus the days that fill the month to the full weeks, e.g.:
        -> if first day of month is tuesday,
        the function will also return a last day of the previous month
        -> if last day of month is friday,
        the function will also return two first days of the next month
    '''
    first = datetime.date(date_.year, date_.month, 1)
    while first.weekday():
        first = first - datetime.timedelta(days=1)
    ## monthrange returns weekday of the first day and number of days in month
    last_day = monthrange(date_.year, date_.month)[1]
    last = datetime.date(date_.year, date_.month, last_day)
    while last.weekday() != 6:
        last = last + datetime.timedelta(days=1)
    days = []
    while first:
        days.append(first)
        if first == last:
            break
        first = first + datetime.timedelta(days=1)
    return days

def fill_week(date_):
    '''
    Function that returns list of days of week for given date.
    '''
    first = date_
    while first.weekday():
        first = first - datetime.timedelta(days=1)
    last = date_
    while last.weekday() != 6:
        last = last + datetime.timedelta(days=1)
    days = []
    while first:
        days.append(first)
        if first == last:
            break
        first = first + datetime.timedelta(days=1)
    return days

def event_dict(event, start, end, from_calendar):
    dict = {
        'pk': event.pk,
        'title': event.title,
        'start': event.start,
        'end': event.end,
        'all_day': event.all_day,
        'color': event.calendar.color,
    }
    if from_calendar == True:
        dict['class'] = event.calendar.pk
        dict['color'] = event.calendar.color
    else:
        dict['class'] = 'other'
        dict['color'] = "#FECA5C"
    if event.all_day != True:
        minutes_in_day = 1440
        end_hour = end.hour
        # if end_hour would be 0
        # then events that end on midnight and after it, would have no height
        if end_hour == 0:
            end_hour = 24
        height = ((end_hour - start.hour) * 60
            + (end.minute - start.minute)) / minutes_in_day
        start_seconds = (start.time().hour * 60
            + start.time().minute)
        top = start_seconds / minutes_in_day
        dict['top'] = top
        dict['height'] = height
    return dict

def get_events_from_days(days, user_events, timezone, profile):
    final_days = []
    for day in days:
        dict_ = {}
        dict_['day'] = day
        start = datetime.datetime.combine(day, datetime.time(0))
        start = timezone.localize(start)
        end = start + datetime.timedelta(days=1)
        events = []
        for ev in user_events:
            calendar = ev.calendar
            if (calendar in profile.get_calendars_to_modify()
                or calendar in profile.get_calendars_to_read()):
                from_calendar = True
            else:
                from_calendar = False
            if ev.start < end and ev.end > start:
                event = event_dict(ev, max(timezone.normalize(ev.start), start),
                    min(timezone.normalize(ev.end), end), from_calendar)
                events.append(event)
        dict_['events'] = events
        final_days.append(dict_)
    return final_days

def get_number_and_name_of_timezone(timezone_source):
    """
    Timezone source must be UserProfile or Event instance.
    """
    return {
        'tz': pytz.timezone(timezone_source.get_timezone_display()),
        'number': timezone_source.timezone,
    }
