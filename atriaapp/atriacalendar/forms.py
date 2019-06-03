from django import forms
from modeltranslation.forms import TranslationModelForm
from django.contrib.auth.forms import UserCreationForm

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

        cur_org = None
        if request:
            if 'URL_NAMESPACE' in request.session and 'organization' in request.session['URL_NAMESPACE']:
                cur_orgs = AtriaOrganization.objects.filter(id=request.session['ACTIVE_ORG'])
                if 0 < len(cur_orgs):
                    cur_org = cur_orgs[0]
            if cur_org:
                # determine current org calendar
                self.fields['calendar'].queryset = AtriaCalendar.objects.filter(org_owner=cur_org)
            elif request.user.is_authenticated:
                # default to user calendar
                self.fields['calendar'].queryset = AtriaCalendar.objects.filter(user_owner=request.user)


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

    def save(self):
        user = super(OrgSignUpForm, self).save()
        if Group.objects.filter(name='Admin').exists():
            user.groups.add(Group.objects.get(name='Admin'))

        return user


class ConnectionForm(forms.Form):
    user_email = forms.CharField()
    org_name = forms.CharField()
    org_id = forms.CharField(label='', widget = forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(ConnectionForm, self).__init__(*args, **kwargs)
        self.fields['user_email'].widget.attrs['readonly'] = True
        self.fields['org_name'].widget.attrs['readonly'] = True

