from django.shortcuts import render

from django.conf import settings

from swingtime.conf import swingtime_settings


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
                  context={'active_view': 'calendar_view', 'year': the_year, 'month': the_month,
                            'languages': settings.LANGUAGES})

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
