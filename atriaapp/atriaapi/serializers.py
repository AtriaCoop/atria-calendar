from rest_framework import serializers
from django.contrib.auth.models import User

from atriacalendar.models import *
from swingtime import models as swingtime_models


class AtriaEventSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=32)
    description = serializers.CharField(max_length=100)
    event_type = serializers.CharField(max_length=4)

class AtriaOccurrenceSerializer(serializers.Serializer):
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    event = AtriaEventSerializer()
