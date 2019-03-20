from django.template import Context, Engine
from django.test import SimpleTestCase
from django.urls import reverse


class DummyRequest:
    """
    Bare-minimum mockup of a request object just to have a session.
    """
    session = {}


class SNURLTests(SimpleTestCase):
    def test_snurl_reverse_view_name(self):
        """
        snurl tag should reverse view name with namespace prepended.
        """
        t = Engine(app_dirs=True, libraries={
            'session_namespaced_url': (
                'atriacalendar.templatetags.session_namespaced_url'),
        }).from_string('{% load session_namespaced_url %}{% snurl "event" %}')
        r = DummyRequest()
        r.session['URL_NAMESPACE'] = 'neighbour:'
        c = Context({"request": r})

        rendered = t.render(c)

        self.assertIn(reverse('neighbour:event'), rendered)
