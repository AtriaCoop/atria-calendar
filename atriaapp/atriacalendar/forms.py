from django import forms
from modeltranslation.forms import TranslationModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils import timezone

from swingtime import models as swingtime_models
from swingtime import forms as swingtime_forms

from .models import *


# class EventForm(TranslationModelForm):
#    """
#    A simple form for adding and updating Event attributes.
#    """
#
#    class Meta:
#        model = Event
#        fields = "__all__"
#
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        self.fields['description'].required = False

class AtriaEventForm(swingtime_forms.EventForm, TranslationModelForm):
    """
    A simple form for adding and updating Event attributes.
    """

    class Meta:
        model = AtriaEvent
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request') if 'request' in kwargs else None

        super(AtriaEventForm, self).__init__(*args, **kwargs)
        self.fields['program'].required = False
        # self.fields['location'].required = False
        self.fields['description'].widget = forms.Textarea()

        cur_org = None
        if request:
            if 'URL_NAMESPACE' in request.session and 'organization' in request.session['URL_NAMESPACE']:
                cur_orgs = AtriaOrganization.objects.filter(id=request.session['ACTIVE_ORG'])
                if 0 < len(cur_orgs):
                    cur_org = cur_orgs[0]
            if cur_org:
                # determine current org calendar
                print("Set calendar query to org_owner", cur_org)
                self.fields['calendar'].queryset = AtriaCalendar.objects.filter(org_owner=cur_org)
            elif request.user.is_authenticated:
                # default to user calendar
                print("Set calendar query to user_owner", request.user)
                self.fields['calendar'].queryset = AtriaCalendar.objects.filter(user_owner=request.user)


class AtriaOccurrenceForm(swingtime_forms.MultipleOccurrenceForm):
    model = AtriaOccurrence


class AtriaEventOccurrenceForm(AtriaEventForm):
    """
    A form that creates an AtriaOccurrence alongside the AtriaEvent.
    """
    day = forms.DateField()
    start_time_delta = forms.TimeField()

    DEFAULT_OCCURRENCE_DURATION = 1  # Hours.

    def __init__(self, *args, **kwargs):
        super(AtriaEventOccurrenceForm, self).__init__(*args, **kwargs)

    def save(self):
        event = super().save()
        start_time = timezone.datetime.combine(
            self.cleaned_data['day'],
            self.cleaned_data['start_time_delta'],
        )
        end_time = start_time +\
            timezone.timedelta(hours=self.DEFAULT_OCCURRENCE_DURATION)

        atriaoccurrence = AtriaOccurrence.objects.create(
            start_time=start_time,
            end_time=end_time,
            event=event,
        )

        return event


class AtriaCopyOccurrenceForm(forms.ModelForm):
    """
    A simple form for adding a duplicate event opportunity
    """
    day = forms.DateField()
    start_time_delta = forms.TimeField()
    occ_id = forms.CharField(label='', widget=forms.HiddenInput())

    DEFAULT_OCCURRENCE_DURATION = 1  # Hours.

    class Meta:
        model = AtriaOccurrence
        fields = ('start_time',)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request') if 'request' in kwargs else None

        super(AtriaCopyOccurrenceForm, self).__init__(*args, **kwargs)

        self.fields['start_time'].required = False

        cur_org = None
        if request:
            if 'URL_NAMESPACE' in request.session and 'organization' in request.session['URL_NAMESPACE']:
                cur_orgs = AtriaOrganization.objects.filter(id=request.session['ACTIVE_ORG'])
                if 0 < len(cur_orgs):
                    cur_org = cur_orgs[0]
            if cur_org:
                pass
            elif request.user.is_authenticated:
                pass

    def save(self):
        prev_occurrence = AtriaOccurrence.objects.get(id=self.cleaned_data['occ_id'])
        start_time = timezone.datetime.combine(
            self.cleaned_data['day'],
            self.cleaned_data['start_time_delta'],
        )
        date_added = timezone.now()

        end_time = start_time +\
            timezone.timedelta(hours=self.DEFAULT_OCCURRENCE_DURATION)

        atriaoccurrence = AtriaOccurrence.objects.create(
            start_time=start_time,
            end_time=end_time,
            event=prev_occurrence.event,
        )

        return atriaoccurrence


class AtriaEventOpportunityForm(forms.ModelForm):
    """
    A simple form for adding volunteer opportunities to events
    """
    day = forms.DateField()
    start_time_delta = forms.TimeField()
    occ_id = forms.CharField(label='', widget=forms.HiddenInput())

    class Meta:
        model = AtriaVolunteerOpportunity
        fields = ('title', 'description', 'start_date')

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request') if 'request' in kwargs else None

        super(AtriaEventOpportunityForm, self).__init__(*args, **kwargs)

        self.fields['description'].widget = forms.Textarea()
        self.fields['start_date'].required = False

        cur_org = None
        if request:
            if 'URL_NAMESPACE' in request.session and 'organization' in request.session['URL_NAMESPACE']:
                cur_orgs = AtriaOrganization.objects.filter(id=request.session['ACTIVE_ORG'])
                if 0 < len(cur_orgs):
                    cur_org = cur_orgs[0]
            if cur_org:
                pass
            elif request.user.is_authenticated:
                pass

    def save(self):
        occurrence = AtriaOccurrence.objects.get(id=self.cleaned_data['occ_id'])
        start_date = timezone.datetime.combine(
            self.cleaned_data['day'],
            self.cleaned_data['start_time_delta'],
        )
        date_added = timezone.now()

        opportunity = AtriaVolunteerOpportunity.objects.create(
            event=occurrence.atriaevent,
            title=self.cleaned_data['title'],
            description=self.cleaned_data['description'],
            start_date=start_date,
            date_added=date_added,
        )

        return opportunity


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False,
                                 help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False,
                                help_text='Optional.')
    email = forms.EmailField(
        max_length=254, help_text='Required. Inform a valid email address.')

    def save(self):
        user = super().save()
        if Group.objects.filter(name='Attendee').exists():
            user.groups.add(Group.objects.get(name='Attendee'))

        return user

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')


class OrgSignUpForm(SignUpForm):
    org_name = forms.CharField(max_length=40, required=True,
                                 help_text='Required.')
    description = forms.CharField(max_length=4000, required=True,
                                 help_text='Required.', widget=forms.Textarea)
    location = forms.CharField(max_length=80, required=True,
                                 help_text='Required.')
    tagline = forms.CharField(max_length=80, required=False)

    def save(self):
        user = super(OrgSignUpForm, self).save()
        if Group.objects.filter(name='Admin').exists():
            user.groups.add(Group.objects.get(name='Admin'))

        return user


class EventAttendanceForm(forms.Form):
    attendee_count = forms.IntegerField(label='', widget=forms.HiddenInput())


class EventVolunteerForm(EventAttendanceForm):
    notes = forms.CharField(label='Message to Volunteer Coordinator:', max_length=4000, required=False)

    def __init__(self, *args, **kwargs):
        super(EventVolunteerForm, self).__init__(*args, **kwargs)
        self.fields['notes'].widget = forms.Textarea()


class ConnectionForm(forms.Form):
    user_email = forms.CharField()
    org_name = forms.CharField()
    org_id = forms.CharField(label='', widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(ConnectionForm, self).__init__(*args, **kwargs)
        self.fields['user_email'].widget.attrs['readonly'] = True
        self.fields['org_name'].widget.attrs['readonly'] = True

