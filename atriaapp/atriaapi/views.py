from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

import asyncio
import json
import uuid
from datetime import datetime, date, timedelta
import calendar

from atriacalendar.models import *
from swingtime import models as swingtime_models

from .serializers import *



###########################################
# API views to support REST services
###########################################
class AtriaCalendarView(APIView):

    def get(self, request):
        calendars = AtriaCalendar.objects.all()
        serializer = AtriaCalendarSerializer(calendars, many=True)
        return Response({"calendars": serializer.data})


class AtriaProgramView(APIView):

    def get(self, request):
        programs = AtriaEventProgram.objects.all()
        serializer = AtriaProgramSerializer(programs, many=True)
        return Response({"programs": serializer.data})


class AtriaEventView(APIView):
    #permission_classes = (IsAuthenticated,)

    def get(self, request):
        events = AtriaEvent.objects.all()
        serializer = AtriaEventSerializer(events, many=True)
        return Response({"events": serializer.data})


def get_event_filters(request):
    atriacalendar = request.GET.get('calendar')
    program = request.GET.get('program')
    return (atriacalendar, program)


def period_occurrences(start, end, atriacalendar=None, program=None):
    occurrences = swingtime_models.Occurrence.objects.filter(
            models.Q(
                start_time__gte=start,
                start_time__lte=end,
            ) |
            models.Q(
                end_time__gte=start,
                end_time__lte=end,
            ) |
            models.Q(
                start_time__lt=start,
                end_time__gt=end
            )).all()
    if atriacalendar:
        occurrences = occurrences.filter(event__atriaevent__calendar__id=atriacalendar).all()
    if program:
        occurrences = occurrences.filter(event__atriaevent__event_program__id=program).all()
    occurrences = occurrences.filter(atriaoccurrence__published=True).all()
    occurrences = occurrences.order_by("start_time")
    serializer = AtriaOccurrenceSerializer(occurrences, many=True)

    return serializer.data


def event_month_view(request, year, month):
    (atriacalendar, program) = get_event_filters(request)

    start_dt = datetime(year, month, 1)
    end_dt = datetime(year, month, calendar.monthrange(year, month)[1])
    start = datetime(start_dt.year, start_dt.month, start_dt.day)
    end = end_dt.replace(hour=23, minute=59, second=59)

    # start on Sunday and end on Saturday
    idx = (start.weekday() + 1) % 7 # MON = 0, SUN = 6 -> SUN = 0 .. SAT = 6
    start = start - timedelta(idx)
    idx = (end.weekday() + 1) % 7 # MON = 0, SUN = 6 -> SUN = 0 .. SAT = idx-6
    end = end + timedelta(7-(idx+1))

    occurrence_data = period_occurrences(start, end, atriacalendar, program)

    return JsonResponse({"year": year, "month": month, "start_dt": start, "end_dt": end,  "occurrences": occurrence_data})


def event_week_view(request, year, month, day):
    (atriacalendar, program) = get_event_filters(request)

    start = datetime(year, month, day)
    end = start + timedelta(weeks=1, seconds=-1)

    occurrence_data = period_occurrences(start, end, atriacalendar, program)

    return JsonResponse({
        "year": year,
        "month": month,
        "start_dt": start,
        "end_dt": end,
        "occurrences": occurrence_data
    })


def event_day_view(request, year, month, day):
    if request.GET.get('week'):
        return event_week_view(request, year, month, day)

    (atriacalendar, program) = get_event_filters(request)

    start_dt = datetime(year, month, day)
    end_dt = start_dt
    start = datetime(start_dt.year, start_dt.month, start_dt.day)
    end = end_dt.replace(hour=23, minute=59, second=59)

    occurrence_data = period_occurrences(start, end, atriacalendar, program)

    return JsonResponse({"year": year, "month": month, "day": day, "start_dt": start, "end_dt": end,  "occurrences": occurrence_data})


