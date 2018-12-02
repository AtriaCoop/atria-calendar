from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.utils import timezone, translation
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from swingtime import forms as swingtime_forms
from swingtime import views as swingtime_views

from .forms import *


class TranslatedFormMixin(object):
    """
    Mixin that translates just the form for a FormView.

    Uses query_parameter attribute to determine which parameter to use for the
    language (defaults to 'language')
    """

    query_parameter = 'language'

    def set_language(self):
        # Changes the language to the one specified by query_parameter
        self.previous_language = translation.get_language()
        query_language = self.request.GET.get(self.query_parameter)

        if query_language:
            translation.activate(query_language)

    def wrap(self, method, *args, **kwargs):
        # Changes the language, calls the wrapped method, then reverts language.
        self.set_language()

        return_value = method(*args, **kwargs)

        translation.activate(self.previous_language)

        return return_value

    def get_form(self, *args, **kwargs):
        # Wraps .get_form() in query_parameter language context.
        return self.wrap(super().get_form, *args, **kwargs)

    def post(self, *args, **kwargs):
        # Wraps .post() in query_parameter language context.
        return self.wrap(super().post, *args, **kwargs)


def login(request):
    """Shell login view."""

    return render(request, 'atriacalendar/login.html')

def calendar_home(request):
    """Home page shell view."""

    return render(request, 'atriacalendar/calendar_home.html',
                  context={'active_view': 'calendar_home'})

def calendar_view(request, *args, **kwargs):
    """Whole Calendar shell view."""

    the_year = kwargs['year']
    the_month = kwargs['month']

    return render(request, 'atriacalendar/calendar_view.html',
                  context={'active_view': 'calendar_view', 'year': the_year, 'month': the_month})

def add_atria_event(
    request,
    template='swingtime/add_event.html',
    event_form_class=AtriaEventForm,
    recurrence_form_class=swingtime_forms.MultipleOccurrenceForm
):
    '''
    Add a new ``Event`` instance and 1 or more associated ``Occurrence``s.

    Context parameters:

    ``dtstart``
        a datetime.datetime object representing the GET request value if present,
        otherwise None

    ``event_form``
        a form object for updating the event

    ``recurrence_form``
        a form object for adding occurrences

    '''
    return swingtime_views.add_event(request, template, event_form_class, recurrence_form_class)

def create_event(request):
    """Create Calendar Event shell view."""

    return render(request, 'atriacalendar/create_event.html',
                  context={'active_view': 'create_event'})

def add_participants(request):
    """Second step of Event creation, adding participants. Shell view."""

    return render(request, 'atriacalendar/add_participants.html')

def event_list(request):
    """List/Manage Calendar Events shell view."""

    return render(request, 'atriacalendar/event_list.html',
                  context={'active_view': 'calendar_list'})

def event_detail(request):
    """Shell view for viewing/editing a single Event."""

    return render(request, 'atriacalendar/event_detail.html')

def event_view(request, pk):
    lang = request.GET.get('event_lang')

    if lang:
        translation.activate(lang)

    return swingtime_views.event_view(request, pk, event_form_class=EventForm,
                                      recurrence_form_class=EventForm)

class EventListView(ListView):
    """
    View for listing all events, or events by type
    """
    model = Event
    paginate_by = 25
    context_object_name = 'events'

    def get_queryset(self):
        if 'event_type' in self.kwargs and self.kwargs['event_type']:
            return Event.objects.filter(event_type=self.kwargs['event_type'])
        else:
            return Event.objects.all()

class EventUpdateView(TranslatedFormMixin, UpdateView):
    """
    View for viewing and updating a single Event.
    """
    form_class = EventForm
    model = Event
    recurrence_form_class = swingtime_forms.MultipleOccurrenceForm
    template_name = 'swingtime/event_detail.html'
    query_parameter = 'event_lang'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        if self.form_class == self.recurrence_form_class:
            # There's been a validation error in the recurrence form
            context_data['recurrence_form'] = context_data['form']
            context_data['event_form'] = EventForm(instance=self.object)
        else:
            context_data['recurrence_form'] = self.recurrence_form_class(
                initial={'dstart': timezone.now()})
            context_data['event_form'] = context_data['form']

        return context_data

    def post(self, *args, **kwargs):
        # Selects correct form class based on POST data.
        # NOTE: lifted from swingtime.views.event_view
        if '_update' in self.request.POST:
            return super().post(*args, **kwargs)
        elif '_add' in self.request.POST:
            self.form_class = self.recurrence_form_class
            return super().post(*args, **kwargs)
        else:
            return HttpResponseBadRequest('Bad Request')
