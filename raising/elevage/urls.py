from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='elevage_home'),
    path('new/', views.nouveau, name='elevage_nouveau'),
    path('elevage/<int:elevage_id>/', views.dashboard, name='elevage_dashboard'),
    path('liste/', views.liste, name='elevage_liste'),
    path('gameover/', views.gameover, name='elevage_gameover'),
]
