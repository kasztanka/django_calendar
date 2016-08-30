from unittest import skip

from django.core.urlresolvers import resolve
from django.contrib.auth.models import User
from django.contrib.auth import get_user
from django.test import TestCase

from .views import index, register, profile
from .models import UserProfile
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
        
        self.assertRedirects(response, '/profile/%s/' % (correct_profile.user.username,))
        
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
        self.url = '/profile/%s/' % (self.correct_profile.user.username,)
        self.template = 'my_calendar/profile.html'
        self.function = profile
    
    def test_passes_correct_profile_to_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['profile'], self.correct_profile)
 

if __name__ == '__main__':
    unittest.main() 