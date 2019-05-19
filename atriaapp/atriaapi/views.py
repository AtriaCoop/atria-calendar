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
class AtriaEventView(APIView):
    #permission_classes = (IsAuthenticated,)

    def get(self, request):
        events = AtriaEvent.objects.all()
        serializer = AtriaEventSerializer(events, many=True)
        return Response({"events": serializer.data})


def event_year_view(request, year):
    pass


def period_occurrences(start, end):
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
            )).all().order_by('start_time')
    serializer = AtriaOccurrenceSerializer(occurrences, many=True)

    return serializer.data


def event_month_view(request, year, month):
    start_dt = datetime(year, month, 1)
    end_dt = datetime(year, month, calendar.monthrange(year, month)[1])
    start = datetime(start_dt.year, start_dt.month, start_dt.day)
    end = end_dt.replace(hour=23, minute=59, second=59)

    # start on Sunday and end on Saturday
    idx = (start.weekday() + 1) % 7 # MON = 0, SUN = 6 -> SUN = 0 .. SAT = 6
    start = start - timedelta(idx)
    idx = (end.weekday() + 1) % 7 # MON = 0, SUN = 6 -> SUN = 0 .. SAT = idx-6
    end = end + timedelta(7-(idx+1))

    occurrence_data = period_occurrences(start, end)

    return JsonResponse({"year": year, "month": month, "start_dt": start, "end_dt": end,  "occurrences": occurrence_data})


def event_week_view(request, year, month, day):
    start = datetime(year, month, day)
    end = start + timedelta(weeks=1) - timedelta(seconds=1)

    occurrence_data = period_occurrences(start, end)

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

    start_dt = datetime(year, month, day)
    end_dt = start_dt
    start = datetime(start_dt.year, start_dt.month, start_dt.day)
    end = end_dt.replace(hour=23, minute=59, second=59)

    occurrence_data = period_occurrences(start, end)

    return JsonResponse({"year": year, "month": month, "day": day, "start_dt": start, "end_dt": end,  "occurrences": occurrence_data})


