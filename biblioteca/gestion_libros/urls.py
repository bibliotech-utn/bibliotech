from django.urls import path
from . import views

app_name = 'gestion_libros'

urlpatterns = [
    path('index/', views.index_libros, name='index_libros'),
    path('crear/', views.crear_libro, name='crear_libro'),
    path('editar/<int:libro_id>/', views.editar_libro, name='editar_libro'),
    path('exportar/', views.exportar_libros_csv, name='exportar_libros_csv'),
    path('importar/', views.importar_libros, name='importar_libros'),
    path('', views.listar_libros, name='listar_libros'),
]