from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path

from atriacalendar.urls import urlpatterns as atriacalendar_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('', include('atriacalendar.urls')),
)
