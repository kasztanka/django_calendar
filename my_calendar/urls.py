from django.conf.urls import url

from . import views


app_name='my_calendar'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register$', views.RegisterView.as_view(), name='register'),
    url(r'^profile/(?P<username>[a-zA-Z0-9@.+-_]+)',
        views.profile, name='profile'),
    url(r'^login', views.user_login, name='user_login'),
    url(r'logout$', views.user_logout, name='user_logout'),
    url(r'^month/(?P<date>[0-9-]+)$', views.month, name='month'),
    url(r'^week/(?P<date>[0-9-]+)$', views.week, name='week'),
    url(r'^day/(?P<date>[0-9-]+)$', views.day, name='day'),
    url(r'^calendar/new$', views.new_calendar, name='new_calendar'),
    url(r'^calendar/(?P<cal_pk>\d+)$',
        views.calendar_view, name='calendar_view'),
    url(r'^event/new/(?P<cal_pk>\d+)$', views.new_event, name='new_event'),
    url(r'^event/(?P<event_pk>\d+)$', views.event_view, name='event_view'),
    url(r'^search/', views.search, name='search'),
]
