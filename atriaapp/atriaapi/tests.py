from datetime import datetime, timedelta
import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from swingtime.models import EventType

from atriacalendar.models import (
    AtriaEvent, AtriaEventProgram, AtriaOccurrence)

DT_FORMAT = '%Y-%m-%dT%H:%M:%S'

User = get_user_model()


class CalendarAPITests(APITestCase):
    def test_get_week_view(self):
        now = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = now + timedelta(hours=1)
        event_type = EventType.objects.create(
            abbr='test',
            label='Test Event Type',
        )
        atria_event = AtriaEvent.objects.create(
            event_program=AtriaEventProgram.objects.create(
                abbr='test',
                label='Test Event Program',
            ),
            event_type=event_type,
        )

        AtriaOccurrence.objects.create(
            start_time=now,
            end_time=end_time,
            event=atria_event,
        )

        sunday = now - timedelta(days=now.isoweekday() % 7)
        response = self.client.get(
            '/api/atria/calendar/%s/%s/%s/?week=true' % (
                sunday.year, sunday.month, sunday.day))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = json.loads(response.content)
        self.assertEqual(data['year'], now.year)
        self.assertEqual(data['month'], now.month)
        self.assertEqual(
            datetime.strptime(data['start_dt'], DT_FORMAT), sunday)
        self.assertEqual(
            datetime.strptime(data['end_dt'], DT_FORMAT),
            sunday + timedelta(weeks=1) - timedelta(seconds=1))
        self.assertEqual(len(data['occurrences']), 1)

        occurrence = data['occurrences'][0]
        self.assertEqual(
            datetime.strptime(occurrence['start_time'], DT_FORMAT), now)
        self.assertEqual(
            datetime.strptime(occurrence['end_time'], DT_FORMAT), end_time)

        event = occurrence['event']
        self.assertEqual(event['title'], atria_event.title)
        self.assertEqual(event['description'], atria_event.description)
        self.assertEqual(event['event_type'], event_type.label)
