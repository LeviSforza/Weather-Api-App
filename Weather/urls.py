from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('pollution/', views.pollution),
    path('forecast/', views.forecast),
    path('currentWeather/', views.currentWeather),
    path('geoCity/', views.geoCity),
]