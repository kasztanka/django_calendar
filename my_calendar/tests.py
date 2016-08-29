from django.core.urlresolvers import resolve
from django.contrib.auth.models import User
from django.contrib.auth import get_user
from django.test import TestCase

from .views import index, register
from .models import UserProfile
from .forms import RegisterForm

class IndexTest(TestCase):
    
    def test_root_url_resolves_to_index_view(self):
        found = resolve('/')
        self.assertEqual(found.func, index)
    
    def test_uses_index_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'my_calendar/index.html')
        
    def test_template_extends_after_base(self):
        response = self.client.get('/')
        self.assertContains(response, "My Calendar")
       
       
class RegisterViewTest(TestCase):
    
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
        response = self.user_registers()
        
        correct_profile = UserProfile.objects.first()
        other_user = User.objects.create()
        other_profile = UserProfile.objects.create(user=other_user)
        
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
    
    def test_uses_register_template(self):
        response = self.client.get('/register')
        self.assertTemplateUsed(response, 'my_calendar/register.html')
        
    def test_template_extends_after_base(self):
        response = self.client.get('/register')
        self.assertContains(response, "My Calendar")

        
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
    
    
class ProfileViewTest(TestCase):

    def setUp(self):
        correct_user = User.objects.create(username='pretty_woman')
        self.correct_profile = UserProfile.objects.create(user=correct_user)
        other_user = User.objects.create()
        self.other_profile = UserProfile.objects.create(user=other_user)
    
    def test_uses_profile_template(self):
        response = self.client.get('/profile/%s/' % (self.correct_profile.user.username,))
        self.assertTemplateUsed(response, 'my_calendar/profile.html')
    
    def test_passes_correct_profile_to_template(self):
        response = self.client.get('/profile/%s/' % (self.correct_profile.user.username,))
        self.assertEqual(response.context['profile'], self.correct_profile)
    