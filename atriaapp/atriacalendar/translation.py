from modeltranslation.translator import translator, TranslationOptions
from swingtime.models import Note, EventType, Event
from .models import AtriaNote, AtriaEventProgram, AtriaEvent


class NoteTranslationOptions(TranslationOptions):
    fields = ('note',)

class AtriaNoteTranslationOptions(TranslationOptions):
    fields = ('metadata',)

class EventTypeTranslationOptions(TranslationOptions):
    fields = ('label',)

class EventTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)

class AtriaEventProgramTranslationOptions(TranslationOptions):
    fields = ('label',)

class AtriaEventTranslationOptions(TranslationOptions):
    fields = ('program',)

translator.register(Note, NoteTranslationOptions)
translator.register(AtriaNote, AtriaNoteTranslationOptions)
translator.register(EventType, EventTypeTranslationOptions)
translator.register(Event, EventTranslationOptions)
translator.register(AtriaEventProgram, AtriaEventProgramTranslationOptions)
translator.register(AtriaEvent, AtriaEventTranslationOptions)
