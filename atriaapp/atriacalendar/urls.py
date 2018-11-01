"""
URL configuration for Atria Calendar app.
"""

from django.urls import path
from django.conf.urls import url, include

from .views import *


urlpatterns = [
    path('login/', login, name='login'),

    path('', calendar_home, name='calendar_home'),
    path('calendar/<int:year>/<int:month>/', calendar_view, name='calendar_view'),

    path('create-event/', create_event, name='create_event'),
    path('create-event/participants/', add_participants,
         name='add_participants'),
    path('event-list/', event_list, name='event_list'),
    path('event-detail/', event_detail, name='event_detail'),
    url(r'^swingtime/', include('swingtime.urls')),
]