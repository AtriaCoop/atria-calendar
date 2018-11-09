from django.contrib.auth.models import Group
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import translation
from django.views.generic.edit import UpdateView

from swingtime.models import Event, EventType

from .forms import EventForm
from .models import User, USER_ROLES
from .views import TranslatedFormMixin


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


class TranslatedFormView(TranslatedFormMixin, UpdateView):
    """
    Simple FormView for testing TranslatedFormMixin.
    """
    form_class = EventForm

    def get_object(self):
        return Event.objects.all()[0]


class TranslationTests(TestCase):
    """
    Translation and partial translation-related tests.
    """

    def setUp(self):
        # Creates a single Event with some translated fields.
        self.factory = RequestFactory()
        event_type = EventType.objects.create(
            abbr="Test",
            label="Test EventType",
        )
        self.event = Event.objects.create(
            title="English Title",
            description="English description",
            event_type=event_type,
        )

        translation.activate('fr')

        self.event.title = "French Title"
        self.event.description = "French description"
        self.event.save()

        translation.activate('en')

    def test_translated_form_mixin_get_form(self):
        # Tests that form is translated in correct language by get_form
        form_view = TranslatedFormView
        request = self.factory.get('')
        request.GET = {form_view.query_parameter: 'en'}
        response = TranslatedFormView.as_view()(request)

        self.assertIn(self.event.title_en, response.context_data['form'].as_p())
        self.assertIn(self.event.description_en,
            response.context_data['form'].as_p())

        request.GET[form_view.query_parameter] = 'fr'
        response = TranslatedFormView.as_view()(request)

        self.assertIn(self.event.title_fr, response.context_data['form'].as_p())
        self.assertIn(self.event.description_fr,
            response.context_data['form'].as_p())


class EventTests(TestCase):
    """
    Tests for creating, retrieving, updating, and deleting Events.
    """

    def setUp(self):
        # Creates a single Event with some translated fields.
        event_type = EventType.objects.create(
            abbr="Test",
            label="Test EventType",
        )
        self.event = Event.objects.create(
            title="English Title",
            description="English description",
            event_type=event_type,
        )

        translation.activate('fr')

        self.event.title = "French Title"
        self.event.description = "French description"
        self.event.save()

        translation.activate('en')

    def test_event_view(self):
        # Tests retrieving the view/edit view for a single Event
        response = self.client.get(
            reverse('swingtime-event', args=(self.event.pk,)))

        self.assertEqual(response.status_code, 200)
