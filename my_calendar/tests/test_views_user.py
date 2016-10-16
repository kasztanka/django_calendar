from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import get_user
from django.test import TestCase

from my_calendar.views import register, profile
from my_calendar.models import UserProfile
from .test_views_base import BaseViewTest


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
