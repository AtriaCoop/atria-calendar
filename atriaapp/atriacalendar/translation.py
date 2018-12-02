from modeltranslation.translator import translator, TranslationOptions
from swingtime.models import Note, EventType, Event
from .models import AtriaEvent


class NoteTranslationOptions(TranslationOptions):
    fields = ('note',)

class EventTypeTranslationOptions(TranslationOptions):
    fields = ('label',)

class EventTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)

class AtriaEventTranslationOptions(TranslationOptions):
    fields = ('program',)

translator.register(Note, NoteTranslationOptions)
translator.register(EventType, EventTypeTranslationOptions)
translator.register(Event, EventTranslationOptions)
translator.register(AtriaEvent, AtriaEventTranslationOptions)
