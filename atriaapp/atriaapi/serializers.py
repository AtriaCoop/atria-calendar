from rest_framework import serializers
from django.contrib.auth.models import User

from atriacalendar.models import *
from swingtime import models as swingtime_models


class AtriaCalendarSerializer(serializers.Serializer):
    calendar_id = serializers.IntegerField(source='id')
    org_owner_id = serializers.SerializerMethodField()
    user_owner_id = serializers.SerializerMethodField()
    calendar_name = serializers.CharField(max_length=40)

    def get_org_owner_id(self, obj):
        org_owner = getattr(obj, 'org_owner', None)
        if org_owner:
            return org_owner.id
        else:
            return None

    def get_user_owner_id(self, obj):
        user_owner = getattr(obj, 'user_owner', None)
        if user_owner:
            return user_owner.id
        else:
            return None


class AtriaProgramSerializer(serializers.Serializer):
    program_id = serializers.IntegerField(source='id')


class AtriaEventSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=32)
    description = serializers.CharField(max_length=100)
    event_type = serializers.CharField(max_length=4)


class AtriaOccurrenceSerializer(serializers.Serializer):
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    event = AtriaEventSerializer()
