from modeltranslation.translator import translator, TranslationOptions
from swingtime.models import Note, EventType, Event


class NoteTranslationOptions(TranslationOptions):
    fields = ('note',)

class EventTypeTranslationOptions(TranslationOptions):
    fields = ('label',)

class EventTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)

translator.register(Note, NoteTranslationOptions)
translator.register(EventType, EventTypeTranslationOptions)
translator.register(Event, EventTranslationOptions)
