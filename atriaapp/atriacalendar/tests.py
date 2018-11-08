from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from .models import User, USER_ROLES


class UserTests(TestCase):
    """
    Tests for Atria custom User class.
    """

    def setUp(self):
        # Creates a single-user test database.

        self.user = User.objects.create(
            email='test@example.com',
            first_name='Test',
            last_name='User',
        )

    def test_has_role(self):
        # Tests user.has_role(role)
        group_name = USER_ROLES[0]

        self.assertFalse(self.user.has_role(group_name))

        self.user.add_role(group_name)

        self.assertTrue(self.user.has_role(group_name))

    def test_roles(self):
        # Tests user.roles
        self.assertEqual(len(tuple(self.user.roles)), 0)

        for group_name in USER_ROLES:
            self.user.add_role(group_name)

        self.assertEqual(tuple(self.user.roles), USER_ROLES)

    def test_add_role(self):
        # Tests user.add-role(role)
        group_name = USER_ROLES[0]

        self.user.add_role(group_name)

        self.assertIn(group_name, self.user.roles)
