from django.urls import path
from . import views

app_name = 'gestion_personal'

urlpatterns = [
    path('dashboard/', views.dashboard_personal, name='dashboard_personal'),
]

