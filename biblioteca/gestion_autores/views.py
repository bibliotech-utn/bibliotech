from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from biblioteca.decorators import es_personal_required
from biblioteca.utils import listar_con_busqueda_paginacion
from .models import Autor
from .forms import AutorForm, UploadExcelForm
from .importadores.autores_importer import importar_autores_desde_excel

@es_personal_required
def index_autores(request):
    """Vista del índice del módulo de autores"""
    return render(request, 'gestion_autores/index.html')

@es_personal_required
def crear_autor(request):
    if request.method == 'POST':
        form = AutorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Autor creado correctamente.')
            return redirect('gestion_autores:listar_autores')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = AutorForm()
    
    return render(request, "gestion_autores/crear_autor.html", {'form': form})

@es_personal_required
def listar_autores(request):
    autores = Autor.objects.all().order_by('apellido', 'nombre')
    
    campos_busqueda = ['nombre', 'apellido']
    page_obj, q = listar_con_busqueda_paginacion(
        request, autores, campos_busqueda, items_por_pagina=10
    )
    
    return render(request, "gestion_autores/listar_autores.html", {
        'page_obj': page_obj,
        'q': q
    })

@es_personal_required
def editar_autor(request, autor_id):
    autor = get_object_or_404(Autor, id=autor_id)
    
    if request.method == 'POST':
        form = AutorForm(request.POST, instance=autor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Autor actualizado correctamente.')
            return redirect('gestion_autores:listar_autores')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = AutorForm(instance=autor)
    
    return render(request, "gestion_autores/editar_autor.html", {'form': form, 'autor': autor})

@es_personal_required
def importar_autores(request):
    """Vista para importar autores desde archivo Excel"""
    from gestion_importaciones.models import HistorialImportacion
    from datetime import datetime
    from django.core.files.storage import default_storage
    import logging
    
    logger = logging.getLogger('gestion_autores')
    
    # Obtener historial para mostrar
    historial = HistorialImportacion.objects.filter(tipo='autores').order_by('-fecha')[:10]
    
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            # Validar que se haya subido un archivo
            if 'archivo_excel' not in request.FILES:
                messages.error(request, 'Debes seleccionar un archivo Excel.')
                return render(request, 'gestion_autores/importar_autores.html', {
                    'form': form,
                    'historial': historial
                })
            
            archivo = request.FILES['archivo_excel']
            
            # Validar que el archivo no esté vacío
            if archivo.size == 0:
                messages.error(request, 'El archivo está vacío. Por favor, selecciona un archivo válido.')
                return render(request, 'gestion_autores/importar_autores.html', {
                    'form': form,
                    'historial': historial
                })
            
            actualizar_existentes = form.cleaned_data.get('actualizar_existentes', False)
            
            try:
                # Guardar el archivo en media/importaciones
                fecha_str = datetime.now().strftime('%Y%m%d_%H%M%S')
                nombre_archivo = f"autores_{fecha_str}_{archivo.name}"
                ruta_archivo = default_storage.save(f'importaciones/autores/{nombre_archivo}', archivo)
                ruta_completa = default_storage.path(ruta_archivo)
                
                try:
                    # Importar autores
                    resultados = importar_autores_desde_excel(
                        ruta_completa,
                        actualizar_existentes=actualizar_existentes
                    )
                    
                    # Crear registro en historial
                    HistorialImportacion.objects.create(
                        tipo='autores',
                        archivo=ruta_archivo,
                        usuario=request.user,
                        registros_importados=resultados['importados'],
                        registros_actualizados=resultados['actualizados'],
                        registros_omitidos=resultados['omitidos'],
                        total_filas=resultados['total_filas'],
                        errores=len(resultados['errores']),
                        detalles_adicionales={}
                    )
                    
                    # Construir mensaje de resultado
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
                    
                    logger.info(f'Importación de autores completada por {request.user.username}: {resultados}')
                    
                    # Actualizar historial
                    historial = HistorialImportacion.objects.filter(tipo='autores').order_by('-fecha')[:10]
                    
                    return render(request, 'gestion_autores/importar_autores.html', {
                        'form': UploadExcelForm(),
                        'resultados': resultados,
                        'historial': historial
                    })
                    
                except Exception as e:
                    # Eliminar archivo si hubo error en la importación
                    if default_storage.exists(ruta_archivo):
                        default_storage.delete(ruta_archivo)
                    logger.error(f'Error al importar autores: {str(e)}', exc_info=True)
                    raise e
                        
            except Exception as e:
                logger.error(f'Error al procesar importación de autores: {str(e)}', exc_info=True)
                messages.error(request, 'Ocurrió un error al importar el archivo. Verificá que el formato sea correcto e intentá nuevamente.')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = UploadExcelForm()
    
    return render(request, 'gestion_autores/importar_autores.html', {
        'form': form,
        'historial': historial
    })