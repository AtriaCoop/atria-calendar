from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone, translation
from django.views.generic.edit import UpdateView

from swingtime.models import EventType

from ..forms import AtriaEventForm
from ..models import AtriaEvent, AtriaEventProgram, AtriaOccurrence, USER_ROLES
from ..views import EventUpdateView, TranslatedFormMixin

User = get_user_model()


ORG_NAMESPACE = 'organization:'


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
    form_class = AtriaEventForm

    def get_object(self):
        return AtriaEvent.objects.all()[0]


class TranslationTests(TestCase):
    """
    Translation and partial translation-related tests.
    """

    def setUp(self):
        # Creates a single Event with some translated fields.
        self.factory = RequestFactory()
        self.form_view = TranslatedFormView

        translation.activate('en')

        event_type = EventType.objects.create(
            abbr="Test",
            label="Test EventType",
        )
        event_program = AtriaEventProgram.objects.create(
            abbr='TEST',
            label='Test Event Program',
        )
        self.event = AtriaEvent.objects.create(
            title="English Title",
            description="English description",
            event_type=event_type,
            event_program=event_program,
        )

        translation.activate('fr')

        self.event.title = "French Title"
        self.event.description = "French description"
        self.event.save()

        translation.activate('en')

    def test_translated_form_mixin_get_form(self):
        # Tests that form is translated in correct language by get_form
        request = self.factory.get('')
        request.GET = {self.form_view.query_parameter: 'en'}
        response = self.form_view.as_view()(request)

        self.assertIn(self.event.title_en,
                      response.context_data['form'].as_p())
        self.assertIn(self.event.description_en,
                      response.context_data['form'].as_p())

        request.GET[self.form_view.query_parameter] = 'fr'
        response = self.form_view.as_view()(request)

        self.assertIn(self.event.title_fr,
                      response.context_data['form'].as_p())
        self.assertIn(self.event.description_fr,
                      response.context_data['form'].as_p())


class EventTests(TestCase):
    """
    Tests for creating, retrieving, updating, and deleting Events.
    """
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

        # Creates a single Event with some translated fields.
        translation.activate('en')

        self.event_type = EventType.objects.create(
            abbr="Test",
            label="Test EventType",
        )
        self.event_program = AtriaEventProgram.objects.create(
            abbr='TEST',
            label='Test Event Program',
        )
        self.event = AtriaEvent.objects.create(
            title="English Title",
            description="English description",
            event_type=self.event_type,
            event_program=self.event_program,
        )

        translation.activate('fr')

        self.event.title = "French Title"
        self.event.description = "French description"
        self.event.save()

        translation.activate('en')

    def login_as_user(self, user):
        # import pdb; pdb.set_trace()
        self.client.login(email=user.email, password=self.PASSWORD)

    def test_create_event(self):
        # Tests creating an Event.
        # TODO
        pass

    def test_retrieve_event(self):
        # Tests retrieving the view/edit view for a single Event.
        response = self.client.get(
            reverse(ORG_NAMESPACE + 'swingtime-event', args=(self.event.pk,)))

        self.assertEqual(response.status_code, 200)

    def test_update_event(self):
        # Tests updating an Event in default language (English).
        post_data = {
            '_update': 'Update',
            'event_type': self.event_type.pk,
            'title': "New English Title",
            'description': "New English Description",
            'event_program': self.event_program.pk,
        }
        url = reverse(ORG_NAMESPACE + 'swingtime-event', args=(self.event.pk,))

        self.login_as_user(self.admin)

        session = self.client.session
        session['URL_NAMESPACE'] = 'organization:'
        session.save()

        response = self.client.post(url, data=post_data)

        self.assertEqual(response.status_code, 302)

        self.event.refresh_from_db()

        self.assertEqual(self.event.title_en, post_data['title'])
        self.assertEqual(self.event.description_en, post_data['description'])

    def test_update_event_fr(self):
        # Tests updating an Event in a different language (French).
        post_data = {
            '_update': 'Update',
            'event_type': self.event_type.pk,
            'title': "New French Title",
            'description': "New French Description",
            'event_program': self.event_program.pk,
        }

        url = reverse(
            ORG_NAMESPACE + 'swingtime-event', args=(self.event.pk,)
        ) + '?%s=fr' % EventUpdateView.query_parameter

        self.login_as_user(self.admin)

        session = self.client.session
        session['URL_NAMESPACE'] = 'organization:'
        session.save()

        response = self.client.post(url, data=post_data)

        self.assertEqual(response.status_code, 302)

        self.event.refresh_from_db()

        self.assertEqual(self.event.title_fr, post_data['title'])
        self.assertEqual(self.event.description_fr, post_data['description'])


class AtriaOccurrenceTests(TestCase):

    def setUp(self):
        self.event = AtriaEvent.objects.create(
            event_type=EventType.objects.create(),
            event_program=AtriaEventProgram.objects.create(),
        )
        start_time = timezone.now() + timezone.timedelta(days=1)
        self.occurrence = AtriaOccurrence.objects.create(
            start_time=start_time,
            end_time=start_time + timezone.timedelta(hours=1),
            event=self.event,
        )

    def test_occurrence_status_draft(self):
        self.assertEquals('draft', self.occurrence.status)

    def test_occurrence_status_past(self):
        self.occurrence.start_time -= timezone.timedelta(days=2)
        self.occurrence.end_time -= timezone.timedelta(days=2)
        self.occurrence.published = True
        self.occurrence.save()

        self.assertEquals('past', self.occurrence.status)

    def test_occurrence_status_1days(self):
        self.occurrence.published = True
        self.occurrence.save()

        self.assertEquals('1+ day', self.occurrence.status)

    def test_occurrence_status_3days(self):
        self.occurrence.start_time += timezone.timedelta(days=2)
        self.occurrence.end_time += timezone.timedelta(days=2)
        self.occurrence.published = True
        self.occurrence.save()

        self.assertEquals('3+ days', self.occurrence.status)

    def test_occurrence_status_today(self):
        self.occurrence.start_time += timezone.timedelta(days=-1, hours=1)
        self.occurrence.end_time += timezone.timedelta(days=-1, hours=1)
        self.occurrence.published = True
        self.occurrence.save()

        self.assertEquals('today', self.occurrence.status)
