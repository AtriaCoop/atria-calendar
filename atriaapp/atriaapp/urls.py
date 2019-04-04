from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url

from atriacalendar.urls import urlpatterns as atriacalendar_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    #url(r'^api-auth/', include('rest_framework.urls')),
    path('api/atria/', include('atriaapi.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('indy/', include('indy_community.urls')),
]

urlpatterns += i18n_patterns(
    path('', include('atriacalendar.urls')),
)
