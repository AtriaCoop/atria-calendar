"""
URL configuration for Atria Calendar app.
"""

from django.urls import path
from swingtime import views as swingtime_views
from .forms import *
from .views import *
from swingtime import views as swingtime_views


urlpatterns = [
    path('login/', login, name='login'),

    path('', calendar_home, name='calendar_home'),
    path('calendar/<int:year>/', swingtime_views.year_view, name='swingtime-yearly-view'),
    path('calendar/<int:year>/<int:month>/', swingtime_views.month_view, name='swingtime-monthly-view'),
    path('calendar/<int:year>/<int:month>/<int:day>/', swingtime_views.day_view, name='swingtime-daily-view'),

    path('create-event/', add_atria_event, name='swingtime-add-event'),
    path('create-event/participants/', add_participants, name='add_participants'),
    path('event-list/', EventListView.as_view(), name='event_list'),
    #path('event-detail/', event_detail, name='event_detail'),
    path('event-detail/<int:pk>/', EventUpdateView.as_view(), name='swingtime-event'),
    path('event-detail/<int:event_pk>/<int:pk>/', swingtime_views.occurrence_view, name='swingtime-occurrence'),
]
