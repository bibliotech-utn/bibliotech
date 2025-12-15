from django.urls import path
from . import views

app_name = "gestion_prestamos"

urlpatterns = [
    path('index/', views.index_prestamos, name='index_prestamos'),
    path('crear/', views.crear_prestamo, name='crear_prestamo'),
    path('devolver/<int:prestamo_id>/', views.devolver_prestamo, name='devolver_prestamo'),
    path('reservas/crear/<int:libro_id>/', views.crear_reserva, name='crear_reserva'),
    path('reservas/listar/', views.listar_reservas, name='listar_reservas'),
    path('reservas/confirmar/<int:reserva_id>/', views.confirmar_reserva, name='confirmar_reserva'),
    path('exportar/', views.exportar_prestamos_csv, name='exportar_prestamos_csv'),
    path('', views.listar_prestamos, name='listar_prestamos'),
]