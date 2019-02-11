from django.contrib.auth import get_user_model
from django.test import TestCase, modify_settings

from ..middleware import URLPermissionsMiddleware

User = get_user_model()


@modify_settings(
    MIDDLEWARE={'append': 'atriacalendar.middleware.URLPermissionsMiddleware'},
    URL_PERMISSIONS={'append': [
        (r'/en/neighbour', ('Volunteer', 'Attendee')),
        (r'/en/organization', ('Admin',)),
    ]},
)
class URLPermissionsMiddlewareTests(TestCase):
    PASSWORD = 'example'

    def setUp(self):
        for role in ('Attendee', 'Volunteer', 'Admin'):
            setattr(self, role.lower(), User.objects.create(
                email='%s@example.com' % role.lower(),
                first_name=role,
                last_name='User'
            ))

            user = getattr(self, role.lower())

            user.add_role(role)
            user.set_password(self.PASSWORD)
            user.save()

    def request_url_as_user(self, user, url):
        # import pdb; pdb.set_trace()
        self.client.login(email=user.email, password=self.PASSWORD)

        return self.client.get(url)

    def test_attendee_ok(self):
        # TODO: change expected status code to 200 once URL is implemented
        response = self.request_url_as_user(self.attendee,
                                            '/en/neighbour')

        self.assertEqual(200, response.status_code)

    def test_attendee_forbidden(self):
        response = self.request_url_as_user(self.attendee,
                                            '/en/organization')

        self.assertEqual(403, response.status_code)

    def test_volunteer_ok(self):
        # TODO: change expected status code to 200 once URL is implemented
        response = self.request_url_as_user(self.volunteer,
                                            '/en/neighbour')

        self.assertEqual(200, response.status_code)

    def test_volunteer_forbidden(self):
        response = self.request_url_as_user(self.volunteer,
                                            '/en/organization')

        self.assertEqual(403, response.status_code)

    def test_admin_ok(self):
        # TODO: change expected status code to 200 once URL is implemented
        response = self.request_url_as_user(self.admin,
                                            '/en/organization')

        self.assertEqual(200, response.status_code)

    def test_admin_forbidden(self):
        response = self.request_url_as_user(self.admin,
                                            '/en/neighbour')

        self.assertEqual(403, response.status_code)
