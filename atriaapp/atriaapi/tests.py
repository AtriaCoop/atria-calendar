from datetime import datetime, timedelta
import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from swingtime.models import EventType

from atriacalendar.models import (
    AtriaEvent, AtriaEventProgram, AtriaOccurrence, AtriaOrganization, AtriaCalendar)

DT_FORMAT = '%Y-%m-%dT%H:%M:%S'
DT_TZ_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

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
        start_dt = datetime.strptime(data['start_dt'], DT_FORMAT)
        start_dt = start_dt.replace(tzinfo=sunday.tzinfo)
        end_dt = datetime.strptime(data['end_dt'], DT_FORMAT)
        end_dt = end_dt.replace(tzinfo=sunday.tzinfo)
        self.assertEqual(data['year'], now.year)
        self.assertEqual(data['month'], now.month)
        self.assertEqual(start_dt, sunday)
        self.assertEqual(
            end_dt, sunday + timedelta(weeks=1) - timedelta(seconds=1))
        self.assertEqual(len(data['occurrences']), 1)

        occurrence = data['occurrences'][0]
        self.assertEqual(
            datetime.strptime(occurrence['start_time'], DT_TZ_FORMAT), now)
        self.assertEqual(
            datetime.strptime(occurrence['end_time'], DT_TZ_FORMAT), end_time)

        event = occurrence['event']
        self.assertEqual(event['title'], atria_event.title)
        self.assertEqual(event['description'], atria_event.description)
        self.assertEqual(event['event_type'], event_type.label)

    def test_get_calendar_program_view(self):
        now = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = now + timedelta(hours=1)

        org1 = AtriaOrganization.objects.create(
            org_name= "Atria Neighbourhood House",
            status= "Active",
            description= "Atria Neighbourhood House test organization",
            location= "Vancouver",
        )
        org1_calendar = AtriaCalendar.objects.create(
            org_owner= org1,
            user_owner= None,
            calendar_name= "Test Events"
        )
        self.assertEqual(org1_calendar.org_owner.id, org1.id)

        org2 = AtriaOrganization.objects.create(
            org_name= "Other Neighbourhood House",
            status= "Active",
            description= "Other Neighbourhood House test organization",
            location= "Vancouver",
        )
        org2_calendar = AtriaCalendar.objects.create(
            org_owner= org2,
            user_owner= None,
            calendar_name= "Test Events"
        )
        self.assertEqual(org2_calendar.org_owner.id, org2.id)

        program_1 = AtriaEventProgram.objects.create(
            abbr= "PRO1",
            label= "Program 1",
        )
        program_2 = AtriaEventProgram.objects.create(
            abbr= "PRO2",
            label= "Program 2",
        )
        program_3 = AtriaEventProgram.objects.create(
            abbr= "PRO3",
            label= "Program 3",
        )

        event_type = EventType.objects.create(
            abbr='test',
            label='Test Event Type',
        )
        atria_event = AtriaEvent.objects.create(
            event_program=program_1,
            calendar=org1_calendar,
            event_type=event_type,
        )

        AtriaOccurrence.objects.create(
            start_time=now,
            end_time=end_time,
            event=atria_event,
        )

        response = self.client.get(
            '/api/atria/calendars/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data['calendars']), 2)

        response = self.client.get(
            '/api/atria/programs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data['programs']), 3)

        sunday = now - timedelta(days=now.isoweekday() % 7)

        response = self.client.get(
            '/api/atria/calendar/%s/%s/%s/?week=true' % (
                sunday.year, sunday.month, sunday.day))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data['occurrences']), 1)

        response = self.client.get(
            '/api/atria/calendar/%s/%s/%s/?week=true&calendar=%s&program=%s' % (
                sunday.year, sunday.month, sunday.day, org1_calendar.id, program_1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data['occurrences']), 1)

        response = self.client.get(
            '/api/atria/calendar/%s/%s/%s/?week=true&calendar=%s&program=%s' % (
                sunday.year, sunday.month, sunday.day, org2_calendar.id, program_1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data['occurrences']), 0)

        response = self.client.get(
            '/api/atria/calendar/%s/%s/%s/?week=true&calendar=%s&program=%s' % (
                sunday.year, sunday.month, sunday.day, org1_calendar.id, program_2.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data['occurrences']), 0)

        response = self.client.get(
            '/api/atria/calendar/%s/%s/%s/?week=true&calendar=%s&program=%s' % (
                sunday.year, sunday.month, sunday.day, org2_calendar.id, program_2.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data['occurrences']), 0)
