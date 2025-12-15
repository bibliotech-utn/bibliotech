from django.urls import path
from . import views

app_name = "gestion_socios"

urlpatterns = [
    path('index/', views.index_socios, name='index_socios'),
    path('crear/', views.crear_socio, name='crear_socio'),
    path('dashboard/', views.dashboard_socio, name='dashboard_socio'),
    path('exportar/', views.exportar_socios_csv, name='exportar_socios_csv'),
    path('importar/', views.importar_socios, name='importar_socios'),
    path('', views.listar_socios, name='listar_socios'),
]
