from modeltranslation.translator import translator, TranslationOptions
from swingtime.models import Note, EventType, Event
from .models import AtriaEventProgram, AtriaEvent, AtriaOrganization


class NoteTranslationOptions(TranslationOptions):
    fields = ('note',)

class EventTypeTranslationOptions(TranslationOptions):
    fields = ('label',)

class EventTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)

class AtriaEventProgramTranslationOptions(TranslationOptions):
    fields = ('label',)

class AtriaEventTranslationOptions(TranslationOptions):
    fields = ('program',)

class AtriaOrganizationTranslationOptions(TranslationOptions):
    fields = ('org_name',)

translator.register(Note, NoteTranslationOptions)
translator.register(EventType, EventTypeTranslationOptions)
translator.register(Event, EventTranslationOptions)
translator.register(AtriaEventProgram, AtriaEventProgramTranslationOptions)
translator.register(AtriaEvent, AtriaEventTranslationOptions)
translator.register(AtriaOrganization, AtriaOrganizationTranslationOptions)
