from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.nouveau, name='elevage_nouveau'),
]
