from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import Group, PermissionsMixin
from django.db import models
from django.utils import timezone

from swingtime import models as swingtime_models


USER_ROLES = (
    'Admin',
    'Volunteer',
    'Attendee',
)


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
    description = models.CharField(max_length=4000)
    location = models.CharField(max_length=80)


# Extend swingtime Event to add some custom fields
class AtriaEvent(swingtime_models.Event):
    org_id = models.ForeignKey(AtriaOrganization, on_delete=models.CASCADE)
    program = models.CharField(max_length=32, blank=True)
    event_program = models.ForeignKey(
        AtriaEventProgram,
        verbose_name='event program',
        on_delete=models.CASCADE
    )
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.title + ", " + self.location


# general announcements from an Org (will show up on a user's feed if they have an org relationship)
class AtriaOrgAnnouncement(models.Model):
    org_id = models.ForeignKey(AtriaOrganization, on_delete=models.CASCADE)
    added_by_user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=80)
    content = models.CharField(max_length=4000)
    date_added = models.DateTimeField(default=timezone.now)
    effective_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True)


# type of user/org relationship, type can be:
#   Member = user is a regular attendee and/or volunteer
#   Staff = user works at org and can maintain org information
#   Admin = user can manage org/user relationships for this org
class RelationType(models.Model):
    relation_type = models.CharField(max_length=20)
    relation_description = models.CharField(max_length=80)


# Association class for user/organization relationship
class AtriaRelationship(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    org_id = models.ForeignKey(AtriaOrganization, on_delete=models.CASCADE)
    relation_type = models.ForeignKey(RelationType, verbose_name='relationship', on_delete=models.CASCADE)
    status = models.CharField(max_length=8)
    effective_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True)


# type of user/event relationship:
#   Bookmark
#   Attend
#   Volunteer
#   Organize (for org staff only)
class EventAttendanceType(models.Model):
    attendance_type = models.CharField(max_length=20)
    attendance_description = models.CharField(max_length=80)


# set of "bookmarked" events (for a user)
class AtriaBookmark(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    event_id = models.ForeignKey(AtriaEvent, on_delete=models.CASCADE)
    bookmark_type = models.ForeignKey(EventAttendanceType, verbose_name='bookmark_type', on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)
    notes = models.CharField(max_length=4000, blank=True)


# event history tracking (for an organization)
# can be related to a specific user, or just a general count of attendees, volunteers etc.
class AtriaEventAttendance(models.Model):
    event_id = models.ForeignKey(AtriaEvent, on_delete=models.CASCADE)
    attendance_type = models.ForeignKey(EventAttendanceType, verbose_name='attendance_type', on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    user_count = models.IntegerField(blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    notes = models.CharField(max_length=4000, blank=True)

