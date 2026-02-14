from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('livres/', views.livre_list, name='livre_list'),
    path('livres/nouveau/', views.livre_create, name='livre_create'),
    path('livres/modifier/<int:pk>/', views.livre_update, name='livre_update'),
    path('livres/supprimer/<int:pk>/', views.livre_delete, name='livre_delete'),
    path('emprunts/', views.emprunt_list, name='emprunt_list'),
    path('emprunts/nouveau/', views.emprunt_create, name='emprunt_create'),
    path('emprunts/modifier/<int:pk>/', views.emprunt_update, name='emprunt_update'),
    path('emprunts/supprimer/<int:pk>/', views.emprunt_delete, name='emprunt_delete'),
]
