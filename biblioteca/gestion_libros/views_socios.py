from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from biblioteca.decorators import es_socio_required
from biblioteca.utils import obtener_socio_desde_user
from gestion_prestamos.models import Prestamo, Reserva
from gestion_prestamos.services import PrestamoService
from gestion_socios.models import Socio
from .models import Libro, Ejemplar
from .services import LibroService

@es_socio_required
def buscar_libros(request):
    """Vista para que los socios busquen libros por género, título o autor"""
    query_titulo = request.GET.get('titulo', '').strip()
    query_autor = request.GET.get('autor', '').strip()
    query_genero = request.GET.get('genero', '').strip()
    
    libros = LibroService.buscar_libros_optimizado(
        titulo=query_titulo or None,
        autor=query_autor or None,
        genero=query_genero or None
    ).order_by('titulo')
    
    generos = LibroService.obtener_generos_disponibles()
    
    libros_con_info = [
        {
            'libro': libro,
            'ejemplares_disponibles': libro.ejemplares_disponibles,
            'total_ejemplares': libro.total_ejemplares,
        }
        for libro in libros
    ]
    
    context = {
        'libros_con_info': libros_con_info,
        'query_titulo': query_titulo,
        'query_autor': query_autor,
        'query_genero': query_genero,
        'generos': generos,
    }
    
    return render(request, 'socios/buscar_libros.html', context)

@es_socio_required
@transaction.atomic
def solicitar_prestamo(request, libro_id):
    """Vista para que un socio solicite un préstamo de un libro"""
    libro = get_object_or_404(Libro.objects.select_related('autor'), id=libro_id)
    
    socio = obtener_socio_desde_user(request.user)
    if not socio:
        messages.error(request, 'No se encontró tu información de socio.')
        return redirect('home')
    
    if not socio.activo:
        messages.error(request, 'Tu cuenta está inactiva. Contacta al administrador.')
        return redirect('home')
    
    puede_prestar, mensaje_error = PrestamoService.validar_limite_prestamos(socio)
    if not puede_prestar:
        messages.error(request, mensaje_error)
        return redirect('socios:buscar_libros')
    
    ejemplar_disponible = Ejemplar.objects.select_for_update().filter(
        libro=libro,
        estado='DISPONIBLE'
    ).first()
    
    if not ejemplar_disponible:
        messages.error(request, 'No hay ejemplares disponibles de este libro.')
        return redirect('socios:buscar_libros')
    
    if request.method == 'POST':
        fecha_devolucion = timezone.now().date() + timedelta(days=30)
        
        try:
            prestamo = PrestamoService.crear_prestamo_seguro(
                socio=socio,
                ejemplar=ejemplar_disponible,
                fecha_devolucion_esperada=fecha_devolucion
            )
            messages.success(request, 'Préstamo registrado correctamente.')
            return redirect('socios:buscar_libros')
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('socios:buscar_libros')
    
    fecha_devolucion = timezone.now().date() + timedelta(days=30)
    context = {
        'libro': libro,
        'ejemplar': ejemplar_disponible,
        'socio': socio,
        'fecha_devolucion': fecha_devolucion,
    }
    
    return render(request, 'socios/solicitar_prestamo.html', context)

@es_socio_required
def mis_prestamos(request):
    """Vista para que los socios vean sus préstamos"""
    socio = obtener_socio_desde_user(request.user)
    if not socio:
        messages.error(request, 'No se encontró tu información de socio.')
        return redirect('home')
    
    prestamos = Prestamo.objects.filter(
        socio=socio
    ).select_related('ejemplar', 'ejemplar__libro').order_by('-fecha_prestamo')
    
    context = {
        'prestamos': prestamos,
        'socio': socio,
    }
    
    return render(request, 'socios/mis_prestamos.html', context)


@es_socio_required
def mis_reservas(request):
    """Vista para que los socios vean sus reservas"""
    socio = obtener_socio_desde_user(request.user)
    if not socio:
        messages.error(request, 'No se encontró tu información de socio.')
        return redirect('home')
    
    reservas = Reserva.objects.filter(
        socio=socio
    ).select_related('libro', 'libro__autor').order_by('-fecha_reserva')
    
    context = {
        'reservas': reservas,
        'socio': socio,
    }
    
    return render(request, 'socios/mis_reservas.html', context)


