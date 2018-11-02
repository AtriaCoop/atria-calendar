from modeltranslation.forms import TranslationModelForm

class AtriaEventForm(TranslationModelForm):
    '''
    A simple form for adding and updating Event attributes

    '''

    class Meta:
        model = Event
        fields = "__all__"

    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
        self.fields['description'].required = False
