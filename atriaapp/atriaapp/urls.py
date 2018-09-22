from django.contrib import admin
from django.urls import include, path

from django.views.generic import TemplateView
from django.conf.urls import url

from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = [
    path('calendar/', include('atriacalendar.urls')),
    url(r'^schedule/', include('schedule.urls')),
    path('admin/', admin.site.urls),
]
