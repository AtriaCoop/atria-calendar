from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import Group, PermissionsMixin
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db import models
from django.utils import timezone
from django.conf import settings

from datetime import datetime, date, timedelta

from swingtime import models as swingtime_models


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


class UserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save()

        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Simple custom User class with email-based login.
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site."
    )
    is_active = models.BooleanField(
        default=True,
        help_text=(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        )
    )
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    objects = UserManager()

    @property
    def roles(self):
        # -> Iterable
        # Produce a list of the given user's roles.

        return filter(self.has_role, USER_ROLES)

    def get_full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def add_role(self, role):
        # String ->
        # Adds user to role group

        self.groups.add(Group.objects.get(name=role))

    def has_role(self, role):
        # String -> Boolean
        # Produce true if user is in the given role group.

        return self.groups.filter(name=role).exists()


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
class AtriaOrganization(models.Model):
    org_name = models.CharField(max_length=40)
    date_joined = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=8)
    description = models.TextField(max_length=4000)
    location = models.CharField(max_length=80)

    def __str__(self):
        return self.org_name + ", " + self.location

    def get_default_calendar(self):
        return self.atriacalendar_set.order_by('id')[0]


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

    def get_for_user(self, user):
        '''
        Returns a queryset of instances that belong to the given user's org.
        '''
        return self.filter(
            event__atriaevent__calendar__org_owner__atriarelationship__user=user)

    def get_for_org_id(self, org_id):
        '''
        Returns a queryset of instances that belong to the given user's org id.
        '''
        return self.filter(
            event__atriaevent__calendar__org_owner__id=org_id)

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
    published = models.BooleanField(default=False)
    publisher = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    objects = AtriaOccurrenceManager()

    @property
    def atriaevent(self):
        return self.event.atriaevent

    @property
    def status(self):
        if not self.published:
            return 'draft'

        days_until = self.days_until()

        if days_until < 0:
            return 'past'
        if days_until > 1:
            return '%s+ days' % days_until
        if days_until == 1:
            return '1+ day'

        return 'today'

    def days_until(self):
        return (self.start_time.date() - timezone.now().date()).days

    @property
    def volunteer_total(self):
        total = self.atriaeventattendance_set\
                .filter(attendance_type__attendance_type='Volunteer')\
                .aggregate(sum=models.Sum('user_count'))['sum']

        return total if total else 0

    @property
    def attendee_total(self):
        total = self.atriaeventattendance_set\
                .filter(attendance_type__attendance_type='Attendee')\
                .aggregate(sum=models.Sum('user_count'))['sum']

        return total if total else 0


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
class AtriaRelationship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    org = models.ForeignKey(AtriaOrganization, on_delete=models.CASCADE)
    relation_type = models.ForeignKey(RelationType, verbose_name='relationship', on_delete=models.CASCADE)
    status = models.CharField(max_length=8)
    effective_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.email + ':' + self.org.org_name + ' = ' + str(self.relation_type)


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


# volunteer opportunity that is available for an event
class AtriaVolunteerOpportunity(models.Model):
    event = models.ForeignKey(AtriaEvent, on_delete=models.CASCADE)
    title = models.TextField(max_length=80, blank=True)
    description = models.TextField(max_length=4000, blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.event) + ':' + self.title


# event history tracking (for an organization)
# can be related to a specific user, or just a general count of attendees, volunteers etc.
class AtriaEventAttendance(models.Model):
    #event = models.ForeignKey(AtriaEvent, on_delete=models.CASCADE)
    occurrence = models.ForeignKey(AtriaOccurrence, on_delete=models.CASCADE, blank=True, null=True)
    attendance_type = models.ForeignKey(EventAttendanceType, on_delete=models.CASCADE)
    volunteer_opportunity = models.ForeignKey(AtriaVolunteerOpportunity, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    user_count = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=timezone.now)
    notes = models.TextField(max_length=4000, blank=True, null=True)

    def __str__(self):
        return str(self.occurrence) + ':' + self.user.email + ' - ' + str(self.attendance_type)


