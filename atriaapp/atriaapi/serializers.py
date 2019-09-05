from rest_framework import serializers
from django.contrib.auth.models import User

from atriacalendar.models import *
from swingtime import models as swingtime_models


class AtriaCalendarSerializer(serializers.Serializer):
    calendar_id = serializers.IntegerField(source='id')
    org_owner_id = serializers.SerializerMethodField()
    org_owner_name = serializers.SerializerMethodField()
    user_owner_id = serializers.SerializerMethodField()
    user_owner_email = serializers.SerializerMethodField()
    calendar_name = serializers.CharField(max_length=40)
    calendar_text = serializers.SerializerMethodField()

    def get_org_owner_id(self, obj):
        org_owner = getattr(obj, 'org_owner', None)
        if org_owner:
            return org_owner.id
        else:
            return None

    def get_org_owner_name(self, obj):
        org_owner = getattr(obj, 'org_owner', None)
        if org_owner:
            return org_owner.org_name
        else:
            return None

    def get_user_owner_id(self, obj):
        user_owner = getattr(obj, 'user_owner', None)
        if user_owner:
            return user_owner.id
        else:
            return None

    def get_user_owner_email(self, obj):
        user_owner = getattr(obj, 'user_owner', None)
        if user_owner:
            return user_owner.email
        else:
            return None

    def get_calendar_text(self, obj):
        if self.get_org_owner_name(obj):
            return self.get_org_owner_name(obj) + ':' + obj.calendar_name
        else:
            return self.get_user_owner_email(obj) + ':' + obj.calendar_name


class AtriaProgramSerializer(serializers.Serializer):
    program_id = serializers.IntegerField(source='id')
    abbr = serializers.CharField()
    label = serializers.CharField()


class AtriaEventSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=32)
    description = serializers.CharField(max_length=100)
    event_type = serializers.CharField(max_length=4)


class AtriaOccurrenceSerializer(serializers.Serializer):
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    event = AtriaEventSerializer()
