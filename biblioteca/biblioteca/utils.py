"""
Utilidades compartidas para el sistema de biblioteca.
"""
import csv
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse


def send_notification_email(destinatario, asunto, mensaje):
    """
    Envía un email de notificación al destinatario.
    
    Args:
        destinatario: Email del destinatario (string)
        asunto: Asunto del email (string)
        mensaje: Cuerpo del mensaje (string)
    """
    send_mail(
        subject=asunto,
        message=mensaje,
        from_email=None,
        recipient_list=[destinatario],
        fail_silently=False,
    )


def exportar_csv_response(filename, headers, data_rows):
    """
    Helper para exportar datos a CSV.
    
    Args:
        filename: Nombre del archivo CSV
        headers: Lista de encabezados
        data_rows: Lista de listas con los datos
    
    Returns:
        HttpResponse con el CSV
    """
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    writer.writerow(headers)
    for row in data_rows:
        writer.writerow(row)
    
    return response


def listar_con_busqueda_paginacion(request, queryset, campos_busqueda, items_por_pagina=10):
    """
    Helper para listar con búsqueda y paginación.
    
    Args:
        request: HttpRequest
        queryset: QuerySet inicial
        campos_busqueda: Lista de campos para buscar (ej: ['nombre', 'apellido'])
        items_por_pagina: Número de items por página (default: 10)
    
    Returns:
        Tuple (page_obj, query_string)
    """
    q = request.GET.get('q', '').strip()
    if q:
        filtros = Q()
        for campo in campos_busqueda:
            filtros |= Q(**{f'{campo}__icontains': q})
        queryset = queryset.filter(filtros)
    
    paginator = Paginator(queryset, items_por_pagina)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return page_obj, q


def obtener_socio_desde_user(user):
    """
    Obtiene el socio asociado a un usuario con manejo de errores.
    
    Usa filter().first() para evitar excepciones DoesNotExist.
    
    Args:
        user: Usuario de Django
    
    Returns:
        Socio o None si no existe
    """
    from gestion_socios.models import Socio
    return Socio.objects.filter(user=user).first()
