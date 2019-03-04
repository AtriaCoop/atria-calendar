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

from atriacalendar.models import *

from .serializers import AtriaEventSerializer


###########################################
# API views to support REST services
###########################################
class AtriaEventView(APIView):
    #permission_classes = (IsAuthenticated,)

    def get(self, request):
        events = AtriaEvent.objects.all()
        serializer = AtriaEventSerializer(events, many=True)
        return Response({"events": serializer.data})

