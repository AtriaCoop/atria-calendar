from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('calendar/', include('atriacalendar.urls')),
    path('admin/', admin.site.urls),
]
