from django.urls import path
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
#from rest_framework_swagger.views import get_swagger_view

from .views import *


#schema_view = get_swagger_view(title='Pastebin API')

app_name = "atriaapi"

# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('events/', AtriaEventView.as_view()),
#    url(r'^$', schema_view),
]