from django.core.urlresolvers import resolve
from django.test import TestCase

from my_calendar.views import index


class BaseViewTest(TestCase):

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
        self.assertEqual(response.status_code, 200)

    def test_template_extends_after_base(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'my_calendar/base.html')

    def user_registers(self, username="John123"):
        response = self.client.post(
            '/register', data={
                'username': username,
                'password': 'password',
                'email': 'example@email.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'timezone': '374',
        })
        return response


if __name__ == '__main__':
    unittest.main()
