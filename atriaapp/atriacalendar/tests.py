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
        # Tests user.has_role
        group_name = 'Admin'
        group = Group.objects.get(name=group_name)

        self.assertFalse(self.user.has_role(group_name))
        self.user.groups.add(group)
        self.assertTrue(self.user.has_role(group_name))

    def test_roles(self):
        # Tests user.roles
        groups = Group.objects.filter(name__in=USER_ROLES)

        self.assertEqual(len(tuple(self.user.roles)), 0)

        for group in groups:
            self.user.groups.add(group)

        self.assertEqual(tuple(self.user.roles), USER_ROLES)
