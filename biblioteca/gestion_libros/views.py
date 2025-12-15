from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from biblioteca.decorators import es_personal_required
from biblioteca.utils import listar_con_busqueda_paginacion, exportar_csv_response
from .models import Libro
from .forms import LibroForm, UploadExcelForm
from .importadores.libros_importer import importar_libros_desde_excel

@es_personal_required
def index_libros(request):
    """Vista del índice del módulo de libros"""
    return render(request, 'gestion_libros/index_libros.html')

@es_personal_required
def crear_libro(request):
    if request.method == 'POST':
        form = LibroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Libro creado correctamente.')
            return redirect('gestion_libros:listar_libros')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = LibroForm()
    
    return render(request, 'gestion_libros/crear_libro.html', {'form': form})

@es_personal_required
def listar_libros(request):
    from django.db.models import Count, Q
    
    libros = Libro.objects.select_related('autor').annotate(
        ejemplares_disponibles=Count(
            'ejemplares',
            filter=Q(ejemplares__estado='DISPONIBLE')
        ),
        total_ejemplares=Count('ejemplares')
    ).all().order_by('titulo')
    
    campos_busqueda = ['titulo', 'autor__nombre', 'autor__apellido', 'genero']
    page_obj, q = listar_con_busqueda_paginacion(
        request, libros, campos_busqueda, items_por_pagina=10
    )
    
    return render(request, 'gestion_libros/listar_libros.html', {'page_obj': page_obj, 'q': q})

@es_personal_required
def editar_libro(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)
    
    if request.method == 'POST':
        form = LibroForm(request.POST, instance=libro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Libro actualizado correctamente.')
            return redirect('gestion_libros:listar_libros')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = LibroForm(instance=libro)
    
    return render(request, 'gestion_libros/editar_libro.html', {'form': form, 'libro': libro})

@es_personal_required
def exportar_libros_csv(request):
    """Exporta todos los libros a un archivo CSV"""
    from django.db.models import Count
    
    headers = ['título', 'autor', 'género', 'isbn', 'fecha_registro', 'cantidad_ejemplares']
    
    libros = Libro.objects.select_related('autor').annotate(
        cantidad_ejemplares=Count('ejemplares')
    ).all().order_by('titulo')
    
    data_rows = []
    for libro in libros:
        autor_completo = f"{libro.autor.nombre} {libro.autor.apellido}"
        data_rows.append([
            libro.titulo,
            autor_completo,
            libro.genero or '',
            libro.isbn or '',
            libro.fecha_registro.strftime('%d/%m/%Y'),
            libro.cantidad_ejemplares
        ])
    
    return exportar_csv_response('libros.csv', headers, data_rows)

@es_personal_required
def importar_libros(request):
    """Vista para importar libros desde archivo Excel"""
    from gestion_importaciones.models import HistorialImportacion
    from datetime import datetime
    from django.core.files.storage import default_storage
    import logging
    
    logger = logging.getLogger('gestion_libros')
    
    # Obtener historial para mostrar
    historial = HistorialImportacion.objects.filter(tipo='libros').order_by('-fecha')[:10]
    
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            # Validar que se haya subido un archivo
            if 'archivo_excel' not in request.FILES:
                messages.error(request, 'Debes seleccionar un archivo Excel.')
                return render(request, 'gestion_libros/importar_libros.html', {
                    'form': form,
                    'historial': historial
                })
            
            archivo = request.FILES['archivo_excel']
            
            # Validar que el archivo no esté vacío
            if archivo.size == 0:
                messages.error(request, 'El archivo está vacío. Por favor, selecciona un archivo válido.')
                return render(request, 'gestion_libros/importar_libros.html', {
                    'form': form,
                    'historial': historial
                })
            
            actualizar_existentes = form.cleaned_data.get('actualizar_existentes', False)
            crear_autores = form.cleaned_data.get('crear_autores', True)
            crear_ejemplares = form.cleaned_data.get('crear_ejemplares', True)
            
            try:
                # Guardar el archivo en media/importaciones
                fecha_str = datetime.now().strftime('%Y%m%d_%H%M%S')
                nombre_archivo = f"libros_{fecha_str}_{archivo.name}"
                ruta_archivo = default_storage.save(f'importaciones/libros/{nombre_archivo}', archivo)
                ruta_completa = default_storage.path(ruta_archivo)
                
                try:
                    resultados = importar_libros_desde_excel(
                        ruta_completa,
                        actualizar_existentes=actualizar_existentes,
                        crear_autores=crear_autores,
                        crear_ejemplares=crear_ejemplares
                    )
                    
                    # Crear registro en historial
                    HistorialImportacion.objects.create(
                        tipo='libros',
                        archivo=ruta_archivo,
                        usuario=request.user,
                        registros_importados=resultados['importados'],
                        registros_actualizados=resultados['actualizados'],
                        registros_omitidos=resultados['omitidos'],
                        total_filas=resultados['total_filas'],
                        errores=len(resultados['errores']),
                        detalles_adicionales={
                            'ejemplares_creados': resultados.get('ejemplares_creados', 0),
                            'autores_creados': resultados.get('autores_creados', 0),
                        }
                    )
                    
                    mensaje = (
                        f"Importación completada. "
                        f"Total filas: {resultados['total_filas']}, "
                        f"Importados: {resultados['importados']}, "
                        f"Actualizados: {resultados['actualizados']}, "
                        f"Omitidos: {resultados['omitidos']}, "
                        f"Ejemplares creados: {resultados['ejemplares_creados']}, "
                        f"Autores creados: {resultados['autores_creados']}"
                    )
                    
                    if resultados['errores']:
                        mensaje += f". Errores: {len(resultados['errores'])}"
                        messages.warning(request, mensaje)
                    else:
                        messages.success(request, mensaje)
                    
                    logger.info(f'Importación de libros completada por {request.user.username}: {resultados}')
                    
                    # Actualizar historial
                    historial = HistorialImportacion.objects.filter(tipo='libros').order_by('-fecha')[:10]
                    
                    return render(request, 'gestion_libros/importar_libros.html', {
                        'form': UploadExcelForm(),
                        'resultados': resultados,
                        'historial': historial
                    })
                    
                except Exception as e:
                    # Eliminar archivo si hubo error en la importación
                    if default_storage.exists(ruta_archivo):
                        default_storage.delete(ruta_archivo)
                    logger.error(f'Error al importar libros: {str(e)}', exc_info=True)
                    raise e
                        
            except Exception as e:
                logger.error(f'Error al procesar importación de libros: {str(e)}', exc_info=True)
                messages.error(request, 'Ocurrió un error al importar el archivo. Verificá que el formato sea correcto e intentá nuevamente.')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = UploadExcelForm()
    
    return render(request, 'gestion_libros/importar_libros.html', {
        'form': form,
        'historial': historial
    })