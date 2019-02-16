"""
URL configuration for Atria Calendar app.
"""

from django.urls import path, include
from .forms import *
from .views import *


# Publicly accessible URL patterns
urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', SignupView.as_view(), name='signup'),
    path('landing_v2', landing_v2, name='landing_v2'),
    path('dashboard_v2', dashboard_v2, name='dashboard_v2'),
    path('', landing_page, name='landing_page')
]

# URL patterns accessible to all authenticated users
calendarpatterns = [
    path('', calendar_home, name='calendar_home'),
    path('calendar', include([
        path('<int:year>/', atria_year_view, name='swingtime-yearly-view'),
        path('<int:year>/', include([
            path('<int:month>/', atria_month_view,
                 name='swingtime-monthly-view'),
            path('<int:month>/<int:day>/', atria_day_view,
                 name='swingtime-daily-view'),
        ])),
    ])),
    path('event-list/', EventListView.as_view(), name='event_list'),
    path('event-detail/', include([
        path('<int:pk>/', EventUpdateView.as_view(), name='swingtime-event'),
        path('<int:event_pk>/<int:pk>/', atria_occurrence_view,
             name='swingtime-occurrence'),
    ])),
]

# URL patterns accessible only to organization Admins
organizationpatterns = [
    path('', include([
        path('create-event/', add_atria_event, name='swingtime-add-event'),
        path('create-event/participants/', add_participants,
             name='add_participants'),
        path('', include((calendarpatterns))),
        ])),
]

urlpatterns.append(path('neighbour/', include((calendarpatterns, 'atriacalendar'), namespace='neighbour')))
urlpatterns.append(path('organization/', include((organizationpatterns, 'atriacalendar'), namespace='organization')))
urlpatterns.append(path('', include(calendarpatterns)))

