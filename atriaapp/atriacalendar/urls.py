from django.urls import path

from . import views


app_name = 'calendar'
urlpatterns = [
    # ex: /calendar/
    path('', views.index, name='index'),
    # ex: /calendar/5/
    path('<int:item_id>/', views.detail, name='detail'),
    # ex: /calendar/5/content/
    path('<int:item_id>/content/', views.content, name='results'),
    # ex: /calendar/5/translate/
    path('<int:item_id>/translate/', views.translate, name='vote'),
]
