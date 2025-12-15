from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.db import transaction
import logging
from biblioteca.decorators import es_personal_required, es_socio_required
from biblioteca.utils import (
    send_notification_email,
    listar_con_busqueda_paginacion,
    exportar_csv_response,
    obtener_socio_desde_user
)
from gestion_socios.models import Socio
from gestion_libros.models import Libro, Ejemplar
from .models import Prestamo, Reserva
from .forms import PrestamoForm
from .services import PrestamoService

logger = logging.getLogger('gestion_prestamos')

@es_personal_required
def index_prestamos(request):
    """Vista del índice del módulo de préstamos"""
    return render(request, 'gestion_prestamos/index_prestamos.html')

@es_personal_required
def crear_prestamo(request):
    if request.method == 'POST':
        form = PrestamoForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    prestamo = form.save()
                messages.success(request, 'Préstamo registrado correctamente.')
                return redirect('gestion_prestamos:listar_prestamos')
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                logger.error(f'Error al crear préstamo: {str(e)}', exc_info=True)
                messages.error(request, 'Ocurrió un error al registrar el préstamo. Por favor, intentá nuevamente.')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = PrestamoForm()
    
    return render(request, "gestion_prestamos/crear_prestamo.html", {'form': form})

@es_personal_required
def listar_prestamos(request):
    prestamos = Prestamo.objects.select_related(
        'socio', 'ejemplar', 'ejemplar__libro'
    ).all().order_by('-fecha_prestamo')
    
    campos_busqueda = [
        'socio__nombre', 'socio__apellido', 'ejemplar__libro__titulo',
        'ejemplar__codigo', 'estado'
    ]
    page_obj, q = listar_con_busqueda_paginacion(
        request, prestamos, campos_busqueda, items_por_pagina=10
    )
    
    return render(request, "gestion_prestamos/listar_prestamos.html", {'page_obj': page_obj, 'q': q})

@es_personal_required
def devolver_prestamo(request, prestamo_id):
    """
    Vista para devolver un préstamo.
    Marca el préstamo como devuelto, actualiza la fecha de devolución real
    y marca el ejemplar como disponible.
    """
    prestamo = get_object_or_404(Prestamo.objects.select_related('ejemplar', 'ejemplar__libro'), id=prestamo_id)
    
    # Verificar que el préstamo no esté ya devuelto
    if prestamo.estado == 'DEVUELTO':
        messages.warning(request, 'Este préstamo ya fue devuelto anteriormente.')
        return redirect('gestion_prestamos:listar_prestamos')
    
    try:
        # Marcar como devuelto usando el método del modelo (actualiza ejemplar.estado a 'DISPONIBLE')
        prestamo.marcar_como_devuelto()
        messages.success(request, 'Préstamo devuelto correctamente.')
    except Exception as e:
        logger.error(f'Error al devolver préstamo {prestamo_id}: {str(e)}', exc_info=True)
        messages.error(request, 'Ocurrió un error al devolver el préstamo. Por favor, intentá nuevamente.')
    
    return redirect('gestion_prestamos:listar_prestamos')

@es_socio_required
def crear_reserva(request, libro_id):
    """Vista para que un socio cree una reserva de un libro"""
    libro = get_object_or_404(Libro.objects.select_related('autor'), id=libro_id)
    
    socio = obtener_socio_desde_user(request.user)
    if not socio:
        messages.error(request, 'No se encontró tu información de socio.')
        return redirect('home')
    
    if not socio.activo:
        messages.error(request, 'Tu cuenta está inactiva. Contacta al administrador.')
        return redirect('home')
    
    ejemplares_disponibles = Ejemplar.objects.filter(
        libro=libro,
        estado='DISPONIBLE'
    ).count()
    
    total_ejemplares = Ejemplar.objects.filter(libro=libro).count()
    
    if ejemplares_disponibles > 0:
        messages.error(request, 'Este libro tiene ejemplares disponibles. No se puede reservar.')
        return redirect('socios:buscar_libros')
    
    reserva_existente = Reserva.objects.filter(
        socio=socio,
        libro=libro,
        estado='PENDIENTE'
    ).exists()
    
    if reserva_existente:
        messages.warning(request, 'Ya tenés una reserva pendiente para este libro.')
        return redirect('socios:buscar_libros')
    
    if request.method == 'POST':
        with transaction.atomic():
            reserva = Reserva.objects.create(
                socio=socio,
                libro=libro,
                estado='PENDIENTE'
            )
        
        if socio.user and socio.user.email:
            try:
                send_notification_email(
                    destinatario=socio.user.email,
                    asunto="Reserva registrada",
                    mensaje=(
                        f"Tu reserva del libro '{libro.titulo}' fue registrada correctamente. "
                        "Disponés de 5 días para retirarlo cuando sea confirmada. "
                        "Recordá presentar tu DNI o ID de socio al momento del retiro."
                    )
                )
            except Exception as e:
                logger.warning(f'Error al enviar email de notificación de reserva: {str(e)}')
        
        messages.success(
            request,
            'Reserva creada correctamente. Disponés de 5 días para retirarla cuando sea confirmada. '
            'Recordá presentar tu DNI o ID de socio al momento del retiro.'
        )
        return redirect('socios:buscar_libros')
    
    context = {
        'libro': libro,
        'socio': socio,
        'total_ejemplares': total_ejemplares,
        'ejemplares_disponibles': ejemplares_disponibles,
    }
    
    return render(request, 'reservas/crear_reserva.html', context)

@es_personal_required
def listar_reservas(request):
    """Vista para listar todas las reservas (solo personal)"""
    reservas = Reserva.objects.select_related(
        'socio', 'libro', 'libro__autor'
    ).all().order_by('-fecha_reserva')
    
    campos_busqueda = ['socio__nombre', 'socio__apellido', 'libro__titulo', 'estado']
    page_obj, q = listar_con_busqueda_paginacion(
        request, reservas, campos_busqueda, items_por_pagina=10
    )
    
    return render(request, 'reservas/listar_reservas.html', {'page_obj': page_obj, 'q': q})


@es_personal_required
def confirmar_reserva(request, reserva_id):
    """Confirma una reserva y notifica al socio"""
    reserva = get_object_or_404(Reserva.objects.select_related('socio__user', 'libro', 'libro__autor'), id=reserva_id)
    
    if reserva.estado != 'PENDIENTE':
        messages.warning(request, 'Solo podés confirmar reservas pendientes.')
        return redirect('gestion_prestamos:listar_reservas')
    
    try:
        with transaction.atomic():
            reserva.estado = 'NOTIFICADA'
            reserva.save(update_fields=['estado'])
            
            if reserva.socio.user and reserva.socio.user.email:
                try:
                    send_notification_email(
                        destinatario=reserva.socio.user.email,
                        asunto="Reserva lista para retirar",
                        mensaje=(
                            f"Tu reserva del libro '{reserva.libro.titulo}' está confirmada. "
                            "Tenés 5 días para retirarla. "
                            "Recordá presentar tu DNI o ID de socio al momento del retiro."
                        )
                    )
                    messages.success(request, 'Reserva confirmada y socio notificado.')
                except Exception as e:
                    logger.warning(f'Error al enviar email de notificación: {str(e)}')
                    messages.success(request, 'Reserva confirmada, pero hubo un problema al enviar la notificación por email.')
    except Exception as e:
        logger.error(f'Error al confirmar reserva {reserva_id}: {str(e)}', exc_info=True)
        messages.error(request, 'Ocurrió un error al confirmar la reserva. Por favor, intentá nuevamente.')
    
    return redirect('gestion_prestamos:listar_reservas')

@es_personal_required
def exportar_prestamos_csv(request):
    """Exporta todos los préstamos a un archivo CSV"""
    headers = [
        'socio', 'libro', 'ejemplar_codigo', 'fecha_prestamo',
        'fecha_devolucion_esperada', 'fecha_devolucion_real', 'estado'
    ]
    
    prestamos = Prestamo.objects.select_related(
        'socio', 'ejemplar', 'ejemplar__libro'
    ).all().order_by('-fecha_prestamo')
    
    data_rows = []
    for prestamo in prestamos:
        socio_completo = f"{prestamo.socio.nombre} {prestamo.socio.apellido}"
        data_rows.append([
            socio_completo,
            prestamo.ejemplar.libro.titulo,
            prestamo.ejemplar.codigo,
            prestamo.fecha_prestamo.strftime('%d/%m/%Y'),
            prestamo.fecha_devolucion_esperada.strftime('%d/%m/%Y'),
            prestamo.fecha_devolucion_real.strftime('%d/%m/%Y') if prestamo.fecha_devolucion_real else '',
            prestamo.estado
        ])
    
    return exportar_csv_response('prestamos.csv', headers, data_rows)