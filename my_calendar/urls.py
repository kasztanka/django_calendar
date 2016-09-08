from django.conf.urls import url

from . import views

app_name='my_calendar'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register$', views.register, name='register'),
    url(r'^profile/(?P<username>[a-zA-Z0-9@.+-_]+)', views.profile, name='profile'),
    url(r'^login', views.user_login, name='user_login'),
    url(r'logout$', views.user_logout, name='user_logout'),
    url(r'month/(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)$', views.month, name='month'),
    url(r'week/(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)$', views.week, name='week'),
    url(r'day/(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)$', views.day, name='day'),
    url(r'^calendar/new$', views.new_calendar, name='new_calendar'),
    url(r'^calendar/(?P<cal_pk>\d+)$', views.calendar_view, name='calendar_view'),
]