"""
URL configuration for Atria Calendar app.
"""

from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings

from .forms import *
from .views import *

USER_NAMESPACE = getattr(settings, "USER_NAMESPACE", 'neighbour')
ORG_NAMESPACE = getattr(settings, "ORG_NAMESPACE", 'organization')

# Publicly accessible URL patterns
urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', SignupView.as_view(), name='signup'),
    path('org_signup/', OrgSignupView.as_view(), name='org_signup'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('contact/', contact_view, name='contact'),
    path('event/', view_event_view, name='view_event'),
    path('opportunity/', view_opportunity_view, name='view_opportunity'),
    path('search_event/', search_event_view, name='search_event'),
    path('search_opportunity/', search_opportunity_view, name='search_opportunity'),
    path('search_neighbour/', search_neighbour_view, name='search_neighbour'),
    path('view_neighbour/', view_neighbour_view, name='view_neighbour'),
    path('view_neighbour/<email>/', view_neighbour_id_view, name='view_neighbour_id'),
    path('search_organization/', search_organization_view, name='search_organization'),
    path('view_organization/', view_organization_view, name='view_organization'),
    path('view_organization/<int:id>/', view_organization_id_view, name='view_organization_id'),
    path('', auth_views.LoginView.as_view(), name='login'),
]

# URL patterns accessible to all authenticated users
calendarpatterns = [
    path('', dashboard_view, name='calendar_home'),
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
    path('create_manage/', CreateManageView.as_view(), name='create_manage'),
    path('<int:occ_id>/opportunity/', manage_opportunity_view, name='opportunity'),
    path('event/', EventCreateView.as_view(), name='event'),
    path('settings/', settings_view, name='settings'),
]

# URL patterns specific to all logged-in users
loggedinuserpatterns = [
    path('connect/', make_connection, name='make_connection'),
]

# URL patterns specific to neighbours
neighbourpatterns = [
    path('', include([
        path('profile/', neighbour_profile_view, name='profile'),
        path('', include(calendarpatterns)),
        path('', include(loggedinuserpatterns)),
        ])),
]

# URL patterns accessible only to organization Admins
organizationpatterns = [
    path('', include([
        path('profile/', organization_profile_view, name='profile'),
        path('create-event/', add_atria_event, name='swingtime-add-event'),
        path('create-event/participants/', add_participants,
             name='add_participants'),
        path('', include(calendarpatterns)),
        path('', include(loggedinuserpatterns)),
        ])),
]

urlpatterns.append(path(USER_NAMESPACE+'/', include((neighbourpatterns, 'atriacalendar'), namespace=USER_NAMESPACE)))
urlpatterns.append(path(ORG_NAMESPACE+'/', include((organizationpatterns, 'atriacalendar'), namespace=ORG_NAMESPACE)))
urlpatterns.append(path('', include(calendarpatterns)))

