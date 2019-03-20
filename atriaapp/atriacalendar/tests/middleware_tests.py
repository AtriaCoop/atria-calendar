from django.contrib.auth import get_user_model
from django.test import TestCase, modify_settings, override_settings

User = get_user_model()


@modify_settings(
    MIDDLEWARE={'append': 'atriacalendar.middleware.URLPermissionsMiddleware'})
@override_settings(URL_NAMESPACE_PERMISSIONS={
        'neighbour': ('Volunteer', 'Attendee'),
        'organization': ('Admin',)
})
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

    def request_url_as_user_with_namespace(self, user, url, namespace):
        self.client.login(email=user.email, password=self.PASSWORD)

        session = self.client.session
        session['URL_NAMESPACE'] = namespace
        session.save()

        return self.client.get(url)

    def test_attendee_ok(self):
        response = self.request_url_as_user_with_namespace(
            self.attendee, '/en/neighbour/', 'neighbour:')

        self.assertEqual(200, response.status_code)

    def test_attendee_forbidden(self):
        response = self.request_url_as_user_with_namespace(
            self.attendee, '/en/organization/', 'neighbour:')

        self.assertEqual(403, response.status_code)

    def test_volunteer_ok(self):
        response = self.request_url_as_user_with_namespace(
            self.volunteer, '/en/neighbour/', 'neighbour:')

        self.assertEqual(200, response.status_code)

    def test_volunteer_forbidden(self):
        response = self.request_url_as_user_with_namespace(
            self.volunteer, '/en/organization/', 'neighbour:')

        self.assertEqual(403, response.status_code)

    def test_admin_ok(self):
        response = self.request_url_as_user_with_namespace(
            self.admin, '/en/organization/', 'organization:')

        self.assertEqual(200, response.status_code)

    def test_admin_forbidden(self):
        response = self.request_url_as_user_with_namespace(
            self.admin, '/en/neighbour/', 'organization:')

        self.assertEqual(403, response.status_code)
