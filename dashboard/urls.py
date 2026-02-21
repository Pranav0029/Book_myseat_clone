from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('theaters/', views.theaters, name='theaters'),
    path('movies_data/', views.movies_data, name='movies_data'),
]
