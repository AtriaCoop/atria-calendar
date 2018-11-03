from modeltranslation.forms import TranslationModelForm
from swingtime.forms import EventForm
from swingtime.models import Event

class AtriaEventForm(TranslationModelForm, EventForm):
    '''
    A simple form for adding and updating Event attributes

    '''

    class Meta:
        model = Event
        fields = "__all__"

    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
        self.fields['description'].required = False
