from django.shortcuts import render
from django.utils import timezone
from biblioteca.decorators import es_personal_required
from gestion_libros.models import Libro, Ejemplar
from gestion_socios.models import Socio
from gestion_prestamos.models import Prestamo

@es_personal_required
def dashboard_personal(request):
    """Dashboard administrativo para el personal de la biblioteca"""
    # Calcular métricas
    total_libros = Libro.objects.count()
    total_ejemplares = Ejemplar.objects.count()
    total_socios = Socio.objects.count()
    
    # Préstamos activos (estado PENDIENTE)
    prestamos_activos = Prestamo.objects.filter(estado='PENDIENTE').count()
    
    # Préstamos vencidos (estado VENCIDO o pendientes con fecha vencida)
    prestamos_vencidos = Prestamo.objects.filter(
        estado='PENDIENTE',
        fecha_devolucion_esperada__lt=timezone.now().date()
    ).count()
    
    # Últimos 5 préstamos
    ultimos_prestamos = Prestamo.objects.select_related(
        'ejemplar', 
        'socio', 
        'ejemplar__libro'
    ).order_by('-fecha_prestamo')[:5]
    
    context = {
        'total_libros': total_libros,
        'total_ejemplares': total_ejemplares,
        'total_socios': total_socios,
        'prestamos_activos': prestamos_activos,
        'prestamos_vencidos': prestamos_vencidos,
        'ultimos_prestamos': ultimos_prestamos,
    }
    
    return render(request, 'gestion_personal/dashboard_personal.html', context)

