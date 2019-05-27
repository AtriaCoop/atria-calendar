from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import Group, PermissionsMixin
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db import models
from django.utils import timezone
from django.conf import settings

from datetime import datetime, date, timedelta

from swingtime import models as swingtime_models

from indy_community.models import IndyUserManager, IndyUser, IndyOrganization, IndyOrgRelationship, IndySchema, AgentConversation


USER_ROLE = getattr(settings, "DEFAULT_USER_ROLE", 'Attendee')
ORG_ROLE = getattr(settings, "DEFAULT_ORG_ROLE", 'Admin')
USER_NAMESPACE = getattr(settings, "USER_NAMESPACE", 'neighbour') + ':'
ORG_NAMESPACE = getattr(settings, "ORG_NAMESPACE", 'organization') + ':'


USER_ROLES = (
    'Admin',
    'Volunteer',
    'Attendee',
)


def url_namespace(role):
    if role == ORG_ROLE:
        return ORG_NAMESPACE
    else:
        return USER_NAMESPACE


def init_user_session(sender, user, request, **kwargs):
    target = request.POST.get('next', '/neighbour/')
    if 'organization' in target:
        if user.has_role(ORG_ROLE):
            orgs = AtriaRelationship.objects.filter(user=user, status="Active", relation_type__is_org_relation=True).all()
            if 0 < len(orgs):
                request.session['ACTIVE_ORG'] = str(orgs[0].org.id)
                request.session['ACTIVE_ROLE'] = ORG_ROLE
            else:
                # TODO for now just set a dummy default - logged in user has no org-enabled role
                request.session['ACTIVE_ROLE'] = USER_ROLE
        else:
            # TODO for now just set a dummy default - logged in user with no role assigned
            request.session['ACTIVE_ROLE'] = USER_ROLE
    else:
        if user.has_role('Volunteer'):
            request.session['ACTIVE_ROLE'] = 'Volunteer'
        elif user.has_role(USER_ROLE):
            request.session['ACTIVE_ROLE'] = USER_ROLE
        else:
            # TODO for now just set a dummy default - logged in user with no role assigned
            request.session['ACTIVE_ROLE'] = USER_ROLE

    role = request.session['ACTIVE_ROLE']
    namespace = url_namespace(role)
    request.session['URL_NAMESPACE'] = namespace


def clear_user_session(sender, user, request, **kwargs):
    if 'ACTIVE_ROLE' in request.session:
        del request.session['ACTIVE_ROLE']
    if 'ACTIVE_ORG' in request.session:
        del request.session['ACTIVE_ORG']
    request.session['URL_NAMESPACE'] = ''


user_logged_in.connect(init_user_session)

user_logged_out.connect(clear_user_session)


class User(IndyUser):
    """
    Simple custom User class with email-based login.
    """

    objects = IndyUserManager()

    def save(self, *args, **kwargs):
        is_new = self.id is None
        super(User, self).save(*args, **kwargs)
        if is_new:
            calendar = AtriaCalendar(user_owner=self, calendar_name='Events')
            calendar.save()


# Code table for event programs - senior, youth, etc.
class AtriaEventProgram(models.Model):
    '''
    Simple ``Program`` classifcation.
    '''
    abbr = models.CharField(max_length=4, unique=True)
    label = models.CharField(max_length=50)

    def __str__(self):
        return self.label


# Base class for organizations that use the Atria platform
class AtriaOrganization(IndyOrganization):
    #org_name = models.CharField(max_length=40)
    date_joined = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=8)
    description = models.TextField(max_length=4000)
    location = models.CharField(max_length=80)

    def __str__(self):
        return self.org_name + ", " + self.location

    def save(self, *args, **kwargs):
        is_new = self.id is None
        super(AtriaOrganization, self).save(*args, **kwargs)
        if is_new:
            calendar = AtriaCalendar(org_owner=self, calendar_name='Events')
            calendar.save()


# collect events into a "calendar" that has a name and owner (can be an org or individual user)
class AtriaCalendar(models.Model):
    org_owner = models.ForeignKey(AtriaOrganization, on_delete=models.CASCADE, blank=True, null=True)
    user_owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    calendar_name = models.CharField(max_length=40, blank=True)

    def __str__(self):
        if self.org_owner:
            owner = str(self.org_owner)
        else:
            owner = str(self.user_owner)
        return owner + ':' + self.calendar_name
    

# Extend swingtime Event to add some custom fields
class AtriaEvent(swingtime_models.Event):
    calendar = models.ForeignKey(AtriaCalendar, on_delete=models.CASCADE, blank=True, null=True)
    program = models.CharField(max_length=32, blank=True)
    event_program = models.ForeignKey(
        AtriaEventProgram,
        verbose_name='event program',
        on_delete=models.CASCADE
    )
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.title + ", " + self.location


class AtriaOccurrenceManager(swingtime_models.OccurrenceManager):

    def period_occurrences(self, start_dt=None, end_dt=None, event=None):
        '''
        Returns a queryset of for instances that have any overlap with a
        particular period.

        * ``*_dt`` may be either a datetime.datetime, datetime.date object, or
          ``None``. If ``None``, default to the current day.

        * ``event`` can be an ``Event`` instance for further filtering.
        '''
        start_dt = start_dt or datetime.now()
        start = datetime(start_dt.year, start_dt.month, start_dt.day)
        end_dt = end_dt or start
        end = end_dt.replace(hour=23, minute=59, second=59)
        qs = self.filter(
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
            )
        )

        return qs.filter(event=event) if event else qs


class AtriaOccurrence(swingtime_models.Occurrence):

    objects = AtriaOccurrenceManager()


# general announcements from an Org (will show up on a user's feed if they have an org relationship)
class AtriaOrgAnnouncement(models.Model):
    org = models.ForeignKey(AtriaOrganization, on_delete=models.CASCADE)
    added_by_user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=80)
    content = models.TextField(max_length=4000)
    date_added = models.DateTimeField(default=timezone.now)
    effective_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.org.org_name + ':' + self.title


# type of user/org relationship, type can be:
#   Member = user is a regular attendee and/or volunteer
#   Staff = user works at org and can maintain org information
#   Admin = user can manage org/user relationships for this org
class RelationType(models.Model):
    relation_type = models.CharField(max_length=20)
    relation_description = models.CharField(max_length=80)
    # used to give user access to login as Org role for this org
    is_org_relation = models.BooleanField(default=False)

    def __str__(self):
        return self.relation_type


# Association class for user/organization relationship
class AtriaRelationship(IndyOrgRelationship):
    #user = models.ForeignKey(User, on_delete=models.CASCADE)
    #org = models.ForeignKey(AtriaOrganization, on_delete=models.CASCADE)
    relation_type = models.ForeignKey(RelationType, verbose_name='relationship', on_delete=models.CASCADE)
    status = models.CharField(max_length=8)
    effective_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.email + ':' + self.org.org_name + ' = ' + str(self.relation_type)


# certifications (or proof of) issued by an org
class MemberCertification(models.Model):
    member = models.ForeignKey(AtriaRelationship, on_delete=models.CASCADE)
    certification_type = models.ForeignKey(IndySchema, on_delete=models.CASCADE)
    # reference is the issued credential or received proof
    reference = models.ForeignKey(AgentConversation, on_delete=models.CASCADE)
    # attributes, if we are the issuer
    certification_data = models.TextField(max_length=4000, blank=True, null=True)
    # verified flag, if we have received a proof
    verified = models.BooleanField(default=True)

    def __str__(self):
        return self.member.user.email + ':' + self.certification_type.schema_name + ' (' + str(self.reference.conversation_type) + ')'


# certifications owned by a Neighbour (can be displayed publicly)
class NeighbourCertification(models.Model):
    certification_type = models.ForeignKey(IndySchema, on_delete=models.CASCADE)
    # reference is the issued credential or received proof
    reference = models.ForeignKey(AgentConversation, on_delete=models.CASCADE)
    publish = models.BooleanField(default=True)


# type of user/event relationship:
#   Bookmark
#   Attend
#   Volunteer
#   Organize (for org staff only)
class EventAttendanceType(models.Model):
    attendance_type = models.CharField(max_length=20)
    attendance_description = models.CharField(max_length=80)

    def __str__(self):
        return self.attendance_type


# set of "bookmarked" events (for a user)
class AtriaBookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(AtriaEvent, on_delete=models.CASCADE)
    bookmark_type = models.ForeignKey(EventAttendanceType, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)
    notes = models.TextField(max_length=4000, blank=True)

    def __str__(self):
        return self.user.email + ':' + str(self.event)


# event history tracking (for an organization)
# can be related to a specific user, or just a general count of attendees, volunteers etc.
class AtriaEventAttendance(models.Model):
    event = models.ForeignKey(AtriaEvent, on_delete=models.CASCADE)
    attendance_type = models.ForeignKey(EventAttendanceType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    user_count = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=timezone.now)
    notes = models.TextField(max_length=4000, blank=True)

    def __str__(self):
        return str(self.event) + ':' + self.user.email + ' - ' + self.attendance_type


