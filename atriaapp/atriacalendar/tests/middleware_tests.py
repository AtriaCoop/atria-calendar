from django.contrib.auth import get_user_model
from django.test import TestCase, modify_settings

from ..middleware import URLPermissionsMiddleware

User = get_user_model()


@modify_settings(
    MIDDLEWARE={'append': 'atriacalendar.middleware.URLPermissionsMiddleware'},
    URL_PERMISSIONS={'append': [
        (r'/neighbour/.*', ('Volunteer', 'Attendee')),
        (r'/organization/.*', ('Admin',)),
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
                                            '/neighbour/dashboard/')

        self.assertEqual(404, response.status_code)

    def test_attendee_forbidden(self):
        response = self.request_url_as_user(self.attendee,
                                            '/organization/dashboard/')

        self.assertEqual(403, response.status_code)

    def test_volunteer_ok(self):
        # TODO: change expected status code to 200 once URL is implemented
        response = self.request_url_as_user(self.volunteer,
                                            '/neighbour/dashboard/')

        self.assertEqual(404, response.status_code)

    def test_volunteer_forbidden(self):
        response = self.request_url_as_user(self.volunteer,
                                            '/organization/dashboard/')

        self.assertEqual(403, response.status_code)

    def test_admin_ok(self):
        # TODO: change expected status code to 200 once URL is implemented
        response = self.request_url_as_user(self.admin,
                                            '/organization/dashboard/')

        self.assertEqual(404, response.status_code)

    def test_admin_forbidden(self):
        response = self.request_url_as_user(self.admin,
                                            '/neighbour/dashboard/')

        self.assertEqual(403, response.status_code)
