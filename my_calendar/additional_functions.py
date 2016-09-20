from calendar import monthrange
import datetime

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
    
def event_dict(event, settings, start, end):
    seconds_in_day = 86400
    height = (end - start).total_seconds() / seconds_in_day
    start_seconds = (start.time().hour * 3600
        + start.time().minute * 60
        + start.time().second)
    top = start_seconds / seconds_in_day
    dict = {
        'event': event,
        'title': settings.title,
        'start': settings.start,
        'end': settings.end,
        'all_day': settings.all_day,
        'height': height,
        'top': top,
    }
    return dict
    
def get_events_from_days(days, user_events, timezone):
    final_days = []
    for day in days:
        dict_ = {}
        dict_['day'] = day
        start = datetime.datetime.combine(day, datetime.time(0))
        start = timezone.localize(start)
        end = start + datetime.timedelta(days=1)
        events = []
        for ev in user_events:
            settings = ev.get_owner_settings()
            if settings.start < end and settings.end >= start:
                event = event_dict(ev, settings,
                    max(settings.start, start),
                    min(settings.end, end))
                events.append(event)
        dict_['events'] = events
        final_days.append(dict_)
    return final_days

