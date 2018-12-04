from modeltranslation.forms import TranslationModelForm

from swingtime import models as swingtime_models
from swingtime import forms as swingtime_forms

from .models import *


#class EventForm(TranslationModelForm):
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

class AtriaMultipleOccurrenceForm(swingtime_forms.MultipleOccurrenceForm, TranslationModelForm):

    class Meta:
        model = swingtime_models.Occurrence
        fields = "__all__"

    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)


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
        #self.fields['location'].required = False


class AtriaSingleOccurrenceForm(swingtime_forms.SingleOccurrenceForm, TranslationModelForm):
    '''
    A simple form for adding and updating single Occurrence attributes

    '''

    class Meta:
        model = swingtime_models.Occurrence
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
