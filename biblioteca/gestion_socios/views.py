from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from biblioteca.decorators import es_personal_required, es_socio_required
from biblioteca.utils import listar_con_busqueda_paginacion, exportar_csv_response
from gestion_prestamos.models import Prestamo, Reserva
from .models import Socio
from .forms import SocioForm, UploadExcelForm
from .importadores.socios_importer import importar_socios_desde_excel

@es_personal_required
def index_socios(request):
    """Vista del índice del módulo de socios"""
    return render(request, 'gestion_socios/index_socios.html')

@es_personal_required
def crear_socio(request):
    if request.method == 'POST':
        form = SocioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Socio creado correctamente.')
            return redirect('gestion_socios:listar_socios')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = SocioForm()
    
    return render(request, 'gestion_socios/crear_socio.html', {'form': form})

@es_personal_required
def listar_socios(request):
    socios = Socio.objects.all().order_by('apellido', 'nombre')
    
    campos_busqueda = ['nombre', 'apellido', 'identificacion', 'email']
    page_obj, q = listar_con_busqueda_paginacion(
        request, socios, campos_busqueda, items_por_pagina=10
    )
    
    return render(request, 'gestion_socios/listar_socios.html', {'page_obj': page_obj, 'q': q})

@es_socio_required
def dashboard_socio(request):
    """Dashboard para socios con información personalizada"""
    from biblioteca.utils import obtener_socio_desde_user
    
    socio = obtener_socio_desde_user(request.user)
    if not socio:
        messages.error(request, 'No se encontró tu información de socio.')
        return redirect('home')
    
    # Préstamos activos (sin fecha de devolución real)
    prestamos_activos = Prestamo.objects.filter(
        socio=socio,
        fecha_devolucion_real__isnull=True
    ).count()
    
    # Préstamos vencidos (sin fecha de devolución real y fecha esperada pasada)
    prestamos_vencidos = Prestamo.objects.filter(
        socio=socio,
        fecha_devolucion_real__isnull=True,
        fecha_devolucion_esperada__lt=timezone.now().date()
    ).count()
    
    # Reservas pendientes
    reservas_pendientes = Reserva.objects.filter(
        socio=socio,
        estado='PENDIENTE'
    ).count()
    
    # Últimos préstamos devueltos (con fecha de devolución real)
    prestamos_historicos = Prestamo.objects.filter(
        socio=socio,
        fecha_devolucion_real__isnull=False
    ).select_related('ejemplar', 'ejemplar__libro').order_by('-fecha_devolucion_real')[:5]
    
    context = {
        'socio': socio,
        'prestamos_activos': prestamos_activos,
        'prestamos_vencidos': prestamos_vencidos,
        'reservas_pendientes': reservas_pendientes,
        'prestamos_historicos': prestamos_historicos,
    }
    
    return render(request, 'gestion_socios/dashboard_socio.html', context)

@es_personal_required
def exportar_socios_csv(request):
    """Exporta todos los socios a un archivo CSV"""
    headers = ['nombre', 'apellido', 'identificacion', 'email', 'activo', 'fecha_registro']
    
    socios = Socio.objects.all().order_by('apellido', 'nombre')
    data_rows = []
    for socio in socios:
        activo_texto = 'Sí' if socio.activo else 'No'
        data_rows.append([
            socio.nombre,
            socio.apellido,
            socio.identificacion,
            socio.email or '',
            activo_texto,
            socio.fecha_registro.strftime('%d/%m/%Y') if socio.fecha_registro else ''
        ])
    
    return exportar_csv_response('socios.csv', headers, data_rows)

@es_personal_required
def importar_socios(request):
    """Vista para importar socios desde archivo Excel"""
    from gestion_importaciones.models import HistorialImportacion
    from datetime import datetime
    from django.core.files.storage import default_storage
    import logging
    
    logger = logging.getLogger('gestion_socios')
    
    # Obtener historial para mostrar
    historial = HistorialImportacion.objects.filter(tipo='socios').order_by('-fecha')[:10]
    
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            # Validar que se haya subido un archivo
            if 'archivo_excel' not in request.FILES:
                messages.error(request, 'Debes seleccionar un archivo Excel.')
                return render(request, 'gestion_socios/importar_socios.html', {
                    'form': form,
                    'historial': historial
                })
            
            archivo = request.FILES['archivo_excel']
            
            # Validar que el archivo no esté vacío
            if archivo.size == 0:
                messages.error(request, 'El archivo está vacío. Por favor, selecciona un archivo válido.')
                return render(request, 'gestion_socios/importar_socios.html', {
                    'form': form,
                    'historial': historial
                })
            
            actualizar_existentes = form.cleaned_data.get('actualizar_existentes', False)
            crear_usuarios = form.cleaned_data.get('crear_usuarios', False)
            
            try:
                # Guardar el archivo en media/importaciones
                fecha_str = datetime.now().strftime('%Y%m%d_%H%M%S')
                nombre_archivo = f"socios_{fecha_str}_{archivo.name}"
                ruta_archivo = default_storage.save(f'importaciones/socios/{nombre_archivo}', archivo)
                ruta_completa = default_storage.path(ruta_archivo)
                
                try:
                    resultados = importar_socios_desde_excel(
                        ruta_completa,
                        actualizar_existentes=actualizar_existentes,
                        crear_usuarios=crear_usuarios
                    )
                    
                    # Crear registro en historial
                    HistorialImportacion.objects.create(
                        tipo='socios',
                        archivo=ruta_archivo,
                        usuario=request.user,
                        registros_importados=resultados['importados'],
                        registros_actualizados=resultados['actualizados'],
                        registros_omitidos=resultados['omitidos'],
                        total_filas=resultados['total_filas'],
                        errores=len(resultados['errores']),
                        detalles_adicionales={}
                    )
                    
                    mensaje = (
                        f"Importación completada. "
                        f"Total filas: {resultados['total_filas']}, "
                        f"Importados: {resultados['importados']}, "
                        f"Actualizados: {resultados['actualizados']}, "
                        f"Omitidos: {resultados['omitidos']}"
                    )
                    
                    if resultados['errores']:
                        mensaje += f". Errores: {len(resultados['errores'])}"
                        messages.warning(request, mensaje)
                    else:
                        messages.success(request, mensaje)
                    
                    logger.info(f'Importación de socios completada por {request.user.username}: {resultados}')
                    
                    # Actualizar historial
                    historial = HistorialImportacion.objects.filter(tipo='socios').order_by('-fecha')[:10]
                    
                    return render(request, 'gestion_socios/importar_socios.html', {
                        'form': UploadExcelForm(),
                        'resultados': resultados,
                        'historial': historial
                    })
                    
                except Exception as e:
                    # Eliminar archivo si hubo error en la importación
                    if default_storage.exists(ruta_archivo):
                        default_storage.delete(ruta_archivo)
                    logger.error(f'Error al importar socios: {str(e)}', exc_info=True)
                    raise e
                        
            except Exception as e:
                logger.error(f'Error al procesar importación de socios: {str(e)}', exc_info=True)
                messages.error(request, 'Ocurrió un error al importar el archivo. Verificá que el formato sea correcto e intentá nuevamente.')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = UploadExcelForm()
    
    return render(request, 'gestion_socios/importar_socios.html', {
        'form': form,
        'historial': historial
    })