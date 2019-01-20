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
        super().__init__(*args, **kwargs)
        self.fields['program'].required = False
        # self.fields['location'].required = False


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False,
                                 help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False,
                                help_text='Optional.')
    email = forms.EmailField(
        max_length=254, help_text='Required. Inform a valid email address.')

    def save(self):
        if Group.objects.filter(name='Attendee').exists():
            user = super().save()

            user.groups.add(Group.objects.get(name='Attendee'))

            return user

        return super().save()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')
