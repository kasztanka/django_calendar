from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import get_user
from django.test import TestCase

from my_calendar.views import register, profile
from my_calendar.models import UserProfile
from .test_views_base import BaseViewTest


class AnonymousUserTest(TestCase):

    def test_redirects_to_index(self):
        urls = ['/pierogi', '/profile/babajaga']
        for url in urls:
            response = self.client.get(url, follow=True)
            self.assertRedirects(response, '/')


class RegisterViewTest(BaseViewTest):

    def setUp(self):
        self.url = '/register'
        self.template = 'my_calendar/register.html'
        self.function = register

    def test_register_saves_new_user(self):
        self.user_registers()
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(UserProfile.objects.count(), 1)
        user_ = UserProfile.objects.first()
        self.assertEqual(user_.user.username, 'John123')
        self.assertEqual(user_.timezone, 374)

    def test_user_logged_in_after_registration(self):
        self.user_registers()
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated())

    def test_redirects_after_valid_registration_to_correct_profile(self):
        other_user = User.objects.create()
        other_profile = UserProfile.objects.create(user=other_user)

        response = self.user_registers()

        ## filter returns query set, so we have to take first element
        correct_profile = UserProfile.objects.filter(
            user=get_user(self.client))[0]

        self.assertRedirects(response, '/profile/{}'.format(
            correct_profile.user.username))

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
        self.assertContains(response, "Wrong timezone was chosen.")


class ProfileViewTest(BaseViewTest):

    def setUp(self):
        self.user_registers('pretty_woman')
        correct_user = User.objects.get(username='pretty_woman')
        self.correct_profile = UserProfile.objects.get(user=correct_user)
        other_user = User.objects.create(username='john')
        self.other_profile = UserProfile.objects.create(user=other_user)
        self.url = '/profile/{}'.format(self.correct_profile.user.username)
        self.template = 'my_calendar/profile.html'
        self.function = profile

    def test_passes_correct_profile_to_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['profile'], self.correct_profile)


class LoginViewTest(TestCase):

    def setUp(self):
        self.username = 'pretty_woman'
        self.password = 'cow'
        self.user = User.objects.create(username=self.username, password=self.password)
        self.user.set_password(self.user.password)
        self.user.save()
        profile = UserProfile.objects.create(user=self.user)
        profile.save()

    def login(self, username, password):
        response = self.client.post(
            '/login', data={
            'username': username,
            'password': password
            }, follow=True)
        return response

    def test_user_can_login(self):
        self.login(self.username, self.password)
        user = get_user(self.client)
        self.assertEqual(user, self.user)

    def test_redirects_to_profile_after_login(self):
        response = self.login(self.username, self.password)
        self.assertRedirects(response, '/profile/' + self.username)

    def test_passes_erros_after_wrong_login(self):
        response = self.login(self.username, 'wrong')
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
                'timezone': '374'
        })
        user = get_user(self.client)
        self.assertNotEqual(user, None)
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)
        user = get_user(self.client)
        self.assertEqual(user, AnonymousUser())


if __name__ == '__main__':
    unittest.main()
