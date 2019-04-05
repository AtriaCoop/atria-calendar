from modeltranslation.translator import translator, TranslationOptions
from swingtime.models import Note, EventType, Event
from indy_community.models import IndyOrganization
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

class IndyOrganizationTranslationOptions(TranslationOptions):
    fields = ('org_name',)

class AtriaOrganizationTranslationOptions(TranslationOptions):
    fields = ()

translator.register(Note, NoteTranslationOptions)
translator.register(EventType, EventTypeTranslationOptions)
translator.register(Event, EventTranslationOptions)
translator.register(AtriaEventProgram, AtriaEventProgramTranslationOptions)
translator.register(AtriaEvent, AtriaEventTranslationOptions)
translator.register(IndyOrganization, IndyOrganizationTranslationOptions)
translator.register(AtriaOrganization, AtriaOrganizationTranslationOptions)
