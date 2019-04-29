from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import timezone, translation
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.urls import reverse
from django.conf import settings

from datetime import datetime

from swingtime import forms as swingtime_forms
from swingtime import views as swingtime_views

import indy_community.models as indy_models
import indy_community.views as indy_views
import indy_community.agent_utils as agent_utils
import indy_community.wallet_utils as wallet_utils
import indy_community.registration_utils as registration_utils

from .forms import *
from .models import *


USER_ROLE = getattr(settings, "DEFAULT_USER_ROLE", 'Attendee')
ORG_ROLE = getattr(settings, "DEFAULT_ORG_ROLE", 'Admin')
USER_NAMESPACE = getattr(settings, "USER_NAMESPACE", 'neighbour') + ':'
ORG_NAMESPACE = getattr(settings, "ORG_NAMESPACE", 'organization') + ':'


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
        # Changes the language, calls the wrapped method, then reverts language
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


####################################################################
# Wrappers around swingtme views:
####################################################################

def atria_year_view(
    request,
    year,
    template='swingtime/yearly_view.html',
    queryset=None
):
    '''

    Context parameters:

    ``year``
        an integer value for the year in questin

    ``next_year``
        year + 1

    ``last_year``
        year - 1

    ``by_month``
        a sorted list of (month, occurrences) tuples where month is a
        datetime.datetime object for the first day of a month and occurrences
        is a (potentially empty) list of values for that month. Only months
        which have at least 1 occurrence is represented in the list

    '''
    return swingtime_views.year_view(request, year, template, queryset)


def atria_month_view(
    request,
    year,
    month,
    template='swingtime/monthly_view.html',
    queryset=None
):
    '''
    Render a tradional calendar grid view with temporal navigation variables.

    Context parameters:

    ``today``
        the current datetime.datetime value

    ``calendar``
        a list of rows containing (day, items) cells, where day is the day of
        the month integer and items is a (potentially empty) list of occurrence
        for the day

    ``this_month``
        a datetime.datetime representing the first day of the month

    ``next_month``
        this_month + 1 month

    ``last_month``
        this_month - 1 month

    '''
    return swingtime_views.month_view(request, year, month, template, queryset)


def atria_day_view(
    request,
    year,
    month,
    day,
    template='swingtime/daily_view.html',
    **params
):
    '''
    See documentation for function``_datetime_view``.

    '''

    namespace = request.session['URL_NAMESPACE']

    return swingtime_views.day_view(request, year, month, day, template,
                                    **params)


def atria_occurrence_view(
    request,
    event_pk,
    pk,
    template='swingtime/occurrence_detail.html',
    form_class=swingtime_forms.SingleOccurrenceForm
):
    '''
    View a specific occurrence and optionally handle any updates.

    Context parameters:

    ``occurrence``
        the occurrence object keyed by ``pk``

    ``form``
        a form object for updating the occurrence
    '''
    return swingtime_views.occurrence_view(request, event_pk, pk, template,
                                           form_class)


@login_required
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
        a datetime.datetime object representing the GET request value if
        present, otherwise None

    ``event_form``
        a form object for updating the event

    ``recurrence_form``
        a form object for adding occurrences

    '''
    return swingtime_views.add_event(request, template, event_form_class,
                                     recurrence_form_class)


####################################################################
# Atria custom views:
####################################################################

class SignupView(CreateView):
    # form_class = SignUpForm
    form_class = SignUpForm
    model = get_user_model()
    template_name = 'registration/signup.html'

    def get_success_url(self):
        return reverse('login')

    def form_valid(self, form):
        self.object = form.save()

        user = self.object
        raw_password = form.cleaned_data.get('password1')

        # create an Indy wallet - derive wallet name from email, and re-use raw password
        user = registration_utils.user_provision(user, raw_password)

        return HttpResponseRedirect(self.get_success_url())


class OrgSignupView(SignupView):
    # form_class = SignUpForm
    form_class = OrgSignUpForm

    def get_success_url(self):
        return reverse('login')

    def form_valid(self, form):
        # call super's method to save user and create user calendar
        super(OrgSignupView, self).form_valid(form)

        user = self.object
        raw_password = form.cleaned_data.get('password1')

        # now create the org and associate with the user
        org_name = form.cleaned_data.get('org_name')
        org_role_name = form.cleaned_data.get('org_role_name')
        org_role, created = indy_models.IndyOrgRole.objects.get_or_create(name=org_role_name)
        description = form.cleaned_data.get('description')
        location = form.cleaned_data.get('location')
        status = 'Active'
        date_joined = datetime.now()
        org = AtriaOrganization(
                org_name=org_name,
                role=org_role,
                description=description,
                location=location,
                status=status,
                date_joined=date_joined
            )
        org.save()
        registration_utils.org_provision(org, raw_password, org_role)

        relation_types = RelationType.objects.filter(relation_type=ORG_ROLE).all()
        if 0 == len(relation_types):
            relation_types = RelationType.objects.all()
        relation = AtriaRelationship(
                user=self.object,
                org=org,
                relation_type=relation_types[0],
                status=status,
                effective_date=date_joined
            )
        relation.save()

        return HttpResponseRedirect(self.get_success_url())


def mobile_request_connection(request):
    # user requests mobile connection to an org
    if request.method == 'POST':
        # generate ivitation and display a QR code
        form = RequestMobileConnectionForm(request.POST)
        if not form.is_valid():
            return render(request, 'indy/form_response.html', {'msg': 'Form error', 'msg_txt': str(form.errors)})
        else:
            cd = form.cleaned_data
            org = cd.get('org')
            email = cd.get('email')
            partner_name = email + ' (mobile)'

            # get requested org and their wallet
            org_wallet = org.wallet

            # mobile user not registered locally
            target_user = None
            their_wallet = None

            # set wallet password
            # TODO vcx_config['something'] = raw_password

            # build the connection and get the invitation data back
            try:
                org_connection = agent_utils.send_connection_invitation(org_wallet, partner_name)

                return render(request, 'registration/mobile_connection_info.html', {'org_name': org.org_name, 'connection_token': org_connection.token})
            except Exception as e:
                # ignore errors for now
                print(" >>> Failed to create request for", org_wallet.wallet_name)
                print(e)
                return render(request, 'indy/form_response.html', {'msg': 'Failed to create request for ' + org_wallet.wallet_name})

    else:
        # populate form and get info from user
        form = RequestMobileConnectionForm(initial={})
        return render(request, 'registration/request_mobile_connection.html', {'form': form})


@login_required
def calendar_home(request):
    """Home page shell view."""

    namespace = request.session['URL_NAMESPACE']

    return render(request, 'atriacalendar/calendar_home.html',
                  context={'active_view': namespace + 'calendar_home'})


def calendar_view(request, *args, **kwargs):
    """Whole Calendar shell view."""

    the_year = kwargs['year']
    the_month = kwargs['month']

    namespace = request.session['URL_NAMESPACE']

    return render(request, 'atriacalendar/calendar_view.html',
                  context={'active_view': namespace + 'calendar_view', 'year': the_year,
                           'month': the_month})


@login_required
def create_event(request):
    """Create Calendar Event shell view."""

    namespace = request.session['URL_NAMESPACE']

    return render(request, 'atriacalendar/create_event.html',
                  context={'active_view': namespace + 'create_event'})


@login_required
def add_participants(request):
    """Second step of Event creation, adding participants. Shell view."""

    return render(request, 'atriacalendar/add_participants.html')


def event_list(request):
    """List/Manage Calendar Events shell view."""

    namespace = request.session['URL_NAMESPACE']

    return render(request, 'atriacalendar/event_list.html',
                  context={'active_view': namespace + 'calendar_list'})


def event_detail(request):
    """Shell view for viewing/editing a single Event."""

    return render(request, 'atriacalendar/event_detail.html')


def event_view(request, pk):
    lang = request.GET.get('event_lang')

    if lang:
        translation.activate(lang)

    return swingtime_views.event_view(request, pk, event_form_class=EventForm,
                                      recurrence_form_class=EventForm)


class EventListView(ListView, LoginRequiredMixin):
    """
    View for listing all events, or events by type
    """
    model = AtriaEvent
    paginate_by = 25
    context_object_name = 'events'

    def get_queryset(self):
        if 'event_type' in self.kwargs and self.kwargs['event_type']:
            return AtriaEvent.objects.filter(
                event_type=self.kwargs['event_type'])
        else:
            return AtriaEvent.objects.all()


class EventUpdateView(TranslatedFormMixin, UpdateView, LoginRequiredMixin):
    """
    View for viewing and updating a single Event.
    """
    form_class = AtriaEventForm
    model = AtriaEvent
    recurrence_form_class = swingtime_forms.MultipleOccurrenceForm
    template_name = 'swingtime/event_detail.html'
    query_parameter = 'event_lang'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        if self.form_class == self.recurrence_form_class:
            # There's been a validation error in the recurrence form
            context_data['recurrence_form'] = context_data['form']
            context_data['event_form'] = AtriaEventForm(instance=self.object, request=self.request)
        else:
            context_data['recurrence_form'] = self.recurrence_form_class(
                initial={'dstart': timezone.now()})
            context_data['event_form'] = AtriaEventForm(instance=self.object, request=self.request)

        return context_data

    def post(self, *args, **kwargs):
        # Selects correct form class based on POST data.
        # NOTE: lifted from swingtime.views.event_view
        # TODO: make the recurrence form POST to a different URL to clean this
        #       up
        if '_update' in self.request.POST:
            return super().post(*args, **kwargs)
        elif '_add' in self.request.POST:
            self.form_class = self.recurrence_form_class
            return super().post(*args, **kwargs)
        else:
            return HttpResponseBadRequest('Bad Request')

    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)


# design v2
def dashboard_view(request):
    return render(request, 'atriacalendar/dashboard.html')

def contact_view(request):
    return render(request, 'atriacalendar/pagesSite/contactPage.html')

def settings_view(request):
    return render(request, 'atriacalendar/pagesSite/settingsPage.html')

def neighbour_profile_view(request):
    return render(request, 'atriacalendar/pagesSite/neighbourPage.html')

def organization_profile_view(request):
    return render(request, 'atriacalendar/pagesSite/organizationPage.html')

def view_neighbour_view(request):
    return render(request, 'atriacalendar/pagesSite/neighbourPage.html')

def view_organization_view(request):
    return render(request, 'atriacalendar/pagesSite/organizationPage.html')

def create_manage_view(request):
    return render(request, 'atriacalendar/pagesSite/createManagePage.html')

def view_event_view(request):
    return render(request, 'atriacalendar/pagesSite/eventView.html')

def view_opportunity_view(request):
    return render(request, 'atriacalendar/pagesSite/opportunityView.html')

def manage_event_view(request):
    return render(request, 'atriacalendar/pagesForms/eventForm.html')

def manage_opportunity_view(request):
    return render(request, 'atriacalendar/pagesForms/opportunityForm.html')

def search_event_view(request):
    return render(request, 'atriacalendar/pagesSearch/eventsSearch.html')

def search_opportunity_view(request):
    return render(request, 'atriacalendar/pagesSearch/opportunitiesSearch.html')

def search_neighbour_view(request):
    return render(request, 'atriacalendar/pagesSearch/neighboursSearch.html')

def search_organization_view(request):
    return render(request, 'atriacalendar/pagesSearch/organizationsSearch.html')
