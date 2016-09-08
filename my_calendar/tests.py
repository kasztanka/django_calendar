import datetime

from django.contrib.auth.models import User, AnonymousUser
from django.core.urlresolvers import resolve
from django.contrib.auth import get_user
from django.test import TestCase

from .views import index, register, profile, month, week, day, new_calendar, calendar_view
from .models import UserProfile, MyCalendar
from .forms import RegisterForm


class BaseTest(TestCase):
    
    def setUp(self):
        self.url = '/'
        self.template = 'my_calendar/index.html'
        self.function = index
    
    def test_url_resolves_to_correct_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func, self.function)
    
    def test_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, self.template)
        
    def test_template_extends_after_base(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'my_calendar/base.html')
       
       
class RegisterViewTest(BaseTest):

    def setUp(self):
        self.url = '/register'
        self.template = 'my_calendar/register.html'
        self.function = register
    
    def user_registers(self):
        response = self.client.post(
            '/register', data={
                'username': 'John123',
                'password': 'password',
                'email': 'example@email.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'timezone': 'UTC'
        })
        return response
    
    def test_register_saves_new_user(self):
        self.user_registers()
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(UserProfile.objects.count(), 1)
        user_ = UserProfile.objects.first()
        self.assertEqual(user_.user.username, 'John123')
        self.assertEqual(user_.timezone, 'UTC')       
    
    def test_user_logged_in_after_registration(self):
        self.user_registers()
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated())
               
    def test_redirects_after_valid_registration_to_correct_profile(self):
        other_user = User.objects.create()
        other_profile = UserProfile.objects.create(user=other_user)
        
        response = self.user_registers()
        
        ## filter returns query set, so we have to take first element
        correct_profile = UserProfile.objects.filter(user=get_user(self.client))[0]
        
        self.assertRedirects(response, '/profile/{}'.format(correct_profile.user.username))
        
    def test_checks_if_timezone_exists(self):
        response = self.client.post(
            '/register', data={
                'username': 'John123',
                'password': 'password',
                'email': 'example@email.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'timezone': 'Fake timezone'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('wrong_timezone' in response.context)
        self.assertContains(response, "Wrong timezone was chosen.")
    
    def test_passes_timezones(self):
        response = self.client.get('/register')
        self.assertTrue('timezones' in response.context)
        
    def test_passes_timezones_when_form_error(self):
        response = self.client.post('/register')
        self.assertTrue('timezones' in response.context)

        
class RegisterFormTest(TestCase):
    
    def test_valid_data(self):
        form = RegisterForm({
            'username': 'John123',
            'password': 'password',
            'email': 'example@email.com',
            'first_name': 'John',
            'last_name': 'Doe',
        })
        self.assertTrue(form.is_valid())
    
    def test_blank_data(self):
        form = RegisterForm()
        self.assertFalse(form.is_valid())
    
    
class ProfileViewTest(BaseTest):

    def setUp(self):
        correct_user = User.objects.create(username='pretty_woman')
        self.correct_profile = UserProfile.objects.create(user=correct_user)
        other_user = User.objects.create()
        self.other_profile = UserProfile.objects.create(user=other_user)
        self.url = '/profile/{}'.format(self.correct_profile.user.username)
        self.template = 'my_calendar/profile.html'
        self.function = profile
    
    def test_passes_correct_profile_to_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['profile'], self.correct_profile)
 

class LoginViewTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(username='pretty_woman', password='cow')
        self.user.set_password(self.user.password)
        self.user.save()
        profile = UserProfile.objects.create(user=self.user)
        profile.save()       
    
    def test_user_can_login(self):
        response = self.client.post(
            '/login', data={
            'username': 'pretty_woman',
            'password': 'cow'
            }, follow=True)
        user = get_user(self.client)
        self.assertEqual(user, self.user)
        self.assertContains(response, "Hey, pretty_woman!")
    
    def test_passes_erros_after_wrong_login(self):
        response = self.client.post(
            '/login', data={
            'username': 'pretty_woman',
            'password': 'bull'
            })
        self.assertTrue('login_errors' in response.context)
        self.assertContains(response, "Wrong username or password.")

        
class LogoutViewTest(TestCase):
    
    def test_user_can_logout(self):
        self.client.post(
            '/register', data={
                'username': 'John123',
                'password': 'password',
                'email': 'example@email.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'timezone': 'UTC'
        })
        user = get_user(self.client)
        self.assertNotEqual(user, None)
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)
        user = get_user(self.client)
        self.assertEqual(user, AnonymousUser())
 
 
class DayViewTest(BaseTest):
    
    def setUp(self):
        self.today = datetime.datetime.now().date()
        self.base_url = '/day'
        self.date_url()
        self.template = 'my_calendar/day.html'
        self.function = day
        
    def date_url(self):
        self.url = self.base_url + '/{}-{}-{}'.format(
            str(self.today.year), str(self.today.month), str(self.today.day))
    
    def passes_days_if_date_is_today(self, response):
        self.assertEqual(self.today, response.context['choosen_date'])

    def test_passes_errors_when_incorrect_date(self):
        response = self.client.get(self.base_url + '/2016-13-01')
        self.assertIn('date-errors', response.context)
        
    def test_passes_today_when_wrong_date(self):
        response = self.client.get(self.base_url + '/2016-13-01')
        self.passes_days_if_date_is_today(response)
    
    def test_passes_date(self):
        response = self.client.get(self.url)
        self.assertIn('choosen_date', response.context)
        
 
class MonthViewTest(DayViewTest):
    
    def setUp(self):
        self.today = datetime.datetime.now().date()
        self.base_url = '/month'
        self.date_url()
        self.template = 'my_calendar/month.html'
        self.function = month
        
    def passes_days_if_date_is_today(self, response):
        first = datetime.date(self.today.year, self.today.month, 1)
        some = datetime.date(self.today.year, self.today.month, 25)
        self.assertIn(first, response.context['days'])
        self.assertIn(some, response.context['days'])
        
    def test_passes_days_of_month_in_context(self):
        response = self.client.get(self.url)
        self.passes_days_if_date_is_today(response)

    def test_passes_correct_days_when_month_given(self):
        response = self.client.get(self.base_url + '/2015-02-01')
        first = datetime.date(2015, 1, 26)
        last = datetime.date(2015, 3, 1)
        self.assertIn(first, response.context['days'])
        self.assertIn(last, response.context['days'])
        self.assertEqual(len(response.context['days']), 35)

class WeekViewTest(DayViewTest):
    
    def setUp(self):
        self.today = datetime.datetime.now().date()
        self.base_url = '/week'
        self.date_url()
        self.template = 'my_calendar/week.html'
        self.function = week
        
    def passes_days_if_date_is_today(self, response):    
        previous = self.today - datetime.timedelta(days=1)
        next = self.today + datetime.timedelta(days=1)
        self.assertTrue(previous in response.context['days']
            or next in response.context['days'])
            
    def test_passes_days_of_week_in_context(self):
        response = self.client.get(self.url)
        self.passes_days_if_date_is_today(response)

    def test_passes_correct_days_when_week_given(self):
        response = self.client.get(self.base_url + '/2015-02-01')
        first = datetime.date(2015, 1, 26)
        last = datetime.date(2015, 2, 1)
        self.assertIn(first, response.context['days'])
        self.assertIn(last, response.context['days'])
        self.assertEqual(len(response.context['days']), 7)
    

class NewCalendarTest(BaseTest):
    
    def setUp(self):
        self.url = '/calendar/new'
        self.template = 'my_calendar/new_calendar.html'
        self.function = new_calendar
    
    def test_saves_calendar(self):
        self.client.post(
            '/register', data={
                'username': 'John123',
                'password': 'password',
                'email': 'example@email.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'timezone': 'UTC'
        })
        self.client.post(
            '/calendar/new', data={
                'name': 'Pretty face',
                'color': '#FF0000',
        })
        self.assertEqual(MyCalendar.objects.count(), 1)
        
    def test_cannot_save_empty_calendar(self):
        self.client.post(
            '/register', data={
                'username': 'John123',
                'password': 'password',
                'email': 'example@email.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'timezone': 'UTC'
        })
        response = self.client.post(
            '/calendar/new', data={
                'name': '',
                'color': '#FF0000',
        })
        self.assertEqual(MyCalendar.objects.count(), 0)
        self.assertIn('errors', response.context)
        
    def test_checks_color_regex(self):
        self.client.post(
            '/register', data={
                'username': 'John123',
                'password': 'password',
                'email': 'example@email.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'timezone': 'UTC'
        })
        response = self.client.post(
            '/calendar/new', data={
                'name': 'Name',
                'color': '#FF000',
        })
        self.assertIn('errors', response.context)
        response = self.client.post(
            '/calendar/new', data={
                'name': 'Name',
                'color': '#FF0ZZZ',
        })
        self.assertIn('errors', response.context)
        response = self.client.post(
            '/calendar/new', data={
                'name': 'Name',
                'color': '2FFE000',
        })
        self.assertIn('errors', response.context)
        self.assertEqual(MyCalendar.objects.count(), 0)
        
    def test_redirects_after_saving_calendar(self):
        self.client.post(
            '/register', data={
                'username': 'John123',
                'password': 'password',
                'email': 'example@email.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'timezone': 'UTC'
        })
        response = self.client.post(
            '/calendar/new', data={
                'name': 'Pretty face',
                'color': '#FF0000',
        })
        calendar_ = MyCalendar.objects.first()
        self.assertRedirects(response, '/calendar/{}'.format(calendar_.pk))
        
        
class CalendarViewTest(BaseTest):

    def setUp(self):
        self.client.post(
            '/register', data={
                'username': 'John123',
                'password': 'password',
                'email': 'example@email.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'timezone': 'UTC'
        })
        profile = UserProfile.objects.get(user=get_user(self.client))
        self.calendar = MyCalendar.objects.create(owner=profile, name="Cindirella", color="E81AD4")
        self.url = '/calendar/1'
        self.template = 'my_calendar/calendar.html'
        self.function = calendar_view
        
        
if __name__ == '__main__':
    unittest.main() 