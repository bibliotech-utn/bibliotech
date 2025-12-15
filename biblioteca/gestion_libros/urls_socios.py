from django.urls import path
from . import views_socios

app_name = 'socios'

urlpatterns = [
    path('buscar/', views_socios.buscar_libros, name='buscar_libros'),
    path('solicitar/<int:libro_id>/', views_socios.solicitar_prestamo, name='solicitar_prestamo'),
    path('mis-prestamos/', views_socios.mis_prestamos, name='mis_prestamos'),
    path('mis-reservas/', views_socios.mis_reservas, name='mis_reservas'),
]


