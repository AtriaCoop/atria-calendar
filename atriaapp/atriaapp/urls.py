from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.conf.urls import url
from django.conf import settings

admin.autodiscover()

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="index.html"),),
    path('calendar/', include('atriacalendar.urls')),
    url(r'^schedule/', include('schedule.urls')),
    url(r'^fullcalendar/', TemplateView.as_view(template_name="fullcalendar.html"), name='fullcalendar'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
