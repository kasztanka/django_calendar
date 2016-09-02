from django.conf.urls import url

from . import views

app_name='my_calendar'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register$', views.register, name='register'),
    url(r'^profile/(?P<username>[a-zA-Z0-9@.+-_]+)/', views.profile, name='profile'),
    url(r'^login', views.user_login, name='user_login'),
    url(r'logout$', views.user_logout, name='user_logout'),
    url(r'month', views.month, name='month'), 
]