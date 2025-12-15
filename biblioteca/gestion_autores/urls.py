from django.urls import path
from . import views

app_name = "gestion_autores"

urlpatterns = [
    path('index/', views.index_autores, name='index_autores'),
    path('crear/', views.crear_autor, name='crear_autor'),
    path('editar/<int:autor_id>/', views.editar_autor, name='editar_autor'),
    path('importar/', views.importar_autores, name='importar_autores'),
    path('', views.listar_autores, name='listar_autores'),
]