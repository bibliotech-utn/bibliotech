"""
Módulo de importación de libros desde archivos Excel.
Permite importar grandes volúmenes de libros de forma optimizada.
Crea autores automáticamente si no existen.
"""
import pandas as pd
from datetime import datetime
from django.db import transaction
from gestion_libros.models import Libro, Ejemplar
from gestion_autores.models import Autor


class LibrosImporter:
    """
    Clase para importar libros desde archivos Excel.
    
    Columnas esperadas en el Excel:
    - titulo (requerido)
    - autor_nombre (requerido)
    - autor_apellido (requerido)
    - isbn (opcional, debe ser único)
    - editorial (opcional)
    - fecha_publicacion (opcional, formato: YYYY-MM-DD o DD/MM/YYYY)
    - numero_paginas (opcional)
    - genero (opcional)
    - cantidad_ejemplares (opcional, default: 1)
    """
    
    COLUMNAS_REQUERIDAS = ['titulo', 'autor_nombre', 'autor_apellido']
    COLUMNAS_OPCIONALES = ['isbn', 'editorial', 'fecha_publicacion', 'numero_paginas', 'genero', 'cantidad_ejemplares']
    
    def __init__(self, archivo_excel):
        """
        Inicializa el importador con el archivo Excel.
        
        Args:
            archivo_excel: Archivo Excel o ruta al archivo
        """
        self.archivo_excel = archivo_excel
        self.resultados = {
            'total_filas': 0,
            'importados': 0,
            'actualizados': 0,
            'omitidos': 0,
            'ejemplares_creados': 0,
            'autores_creados': 0,
            'errores': []
        }
    
    def _normalizar_fecha(self, valor):
        """Normaliza diferentes formatos de fecha a objeto date."""
        if pd.isna(valor) or valor is None or valor == '':
            return None
        
        if isinstance(valor, (datetime, pd.Timestamp)):
            return valor.date() if hasattr(valor, 'date') else valor
        
        if isinstance(valor, str):
            valor = valor.strip()
            if not valor:
                return None
            
            formatos = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
            for formato in formatos:
                try:
                    return datetime.strptime(valor, formato).date()
                except ValueError:
                    continue
            
            try:
                return pd.to_datetime(valor).date()
            except:
                pass
        
        return None
    
    def _limpiar_texto(self, valor):
        """Limpia y normaliza texto."""
        if pd.isna(valor) or valor is None:
            return None
        texto = str(valor).strip()
        return texto if texto else None
    
    def _limpiar_isbn(self, valor):
        """Limpia y normaliza ISBN."""
        isbn = self._limpiar_texto(valor)
        if isbn:
            isbn = isbn.replace('-', '').replace(' ', '')
        return isbn
    
    def _validar_numero(self, valor, default=None):
        """Convierte valor a número entero."""
        if pd.isna(valor) or valor is None or valor == '':
            return default
        
        try:
            return int(float(valor))
        except (ValueError, TypeError):
            return default
    
    def _obtener_o_crear_autor(self, nombre, apellido):
        """
        Obtiene un autor existente o lo crea si no existe.
        
        Args:
            nombre: Nombre del autor
            apellido: Apellido del autor
        
        Returns:
            Autor instance
        """
        autor = Autor.objects.filter(
            nombre__iexact=nombre,
            apellido__iexact=apellido
        ).first()
        
        if not autor:
            autor = Autor.objects.create(
                nombre=nombre.title(),
                apellido=apellido.title()
            )
            self.resultados['autores_creados'] += 1
        
        return autor
    
    def _crear_ejemplares(self, libro, cantidad, codigo_base=None):
        """
        Crea ejemplares para un libro.
        
        Args:
            libro: Instancia de Libro
            cantidad: Cantidad de ejemplares a crear
            codigo_base: Base para el código del ejemplar (opcional)
        """
        if cantidad <= 0:
            return
        
        ejemplares_a_crear = []
        
        # Obtener el último código usado para este libro
        ultimo_ejemplar = Ejemplar.objects.filter(
            libro=libro
        ).order_by('-codigo').first()
        
        # Determinar código inicial
        if ultimo_ejemplar and ultimo_ejemplar.codigo.isdigit():
            ultimo_numero = int(ultimo_ejemplar.codigo)
        else:
            ultimo_numero = 0
        
        # Generar códigos para los nuevos ejemplares
        for i in range(1, cantidad + 1):
            nuevo_numero = ultimo_numero + i
            
            if codigo_base:
                codigo = f"{codigo_base}-{nuevo_numero}"
            else:
                codigo = f"{libro.id or 'TEMP'}-EJ-{nuevo_numero}"
            
            # Asegurar unicidad
            codigo_final = codigo
            contador = 1
            while Ejemplar.objects.filter(codigo=codigo_final).exists():
                codigo_final = f"{codigo}-{contador}"
                contador += 1
            
            ejemplares_a_crear.append(Ejemplar(
                libro=libro,
                codigo=codigo_final,
                estado='DISPONIBLE'
            ))
        
        if ejemplares_a_crear:
            Ejemplar.objects.bulk_create(ejemplares_a_crear)
            self.resultados['ejemplares_creados'] += len(ejemplares_a_crear)
    
    def _validar_fila(self, fila_num, datos):
        """
        Valida una fila de datos.
        
        Args:
            fila_num: Número de fila (para mensajes de error)
            datos: Diccionario con los datos de la fila
        
        Returns:
            Tuple (es_valida: bool, datos_limpios: dict, error: str)
        """
        errores = []
        
        # Validar campos requeridos
        titulo = self._limpiar_texto(datos.get('titulo'))
        autor_nombre = self._limpiar_texto(datos.get('autor_nombre'))
        autor_apellido = self._limpiar_texto(datos.get('autor_apellido'))
        
        if not titulo:
            errores.append("Título es requerido")
        if not autor_nombre:
            errores.append("Nombre del autor es requerido")
        if not autor_apellido:
            errores.append("Apellido del autor es requerido")
        
        if errores:
            return False, None, f"Fila {fila_num + 2}: {', '.join(errores)}"
        
        # Validar ISBN si está presente
        isbn = self._limpiar_isbn(datos.get('isbn'))
        if isbn:
            # Verificar si el ISBN ya existe
            if Libro.objects.filter(isbn=isbn).exists():
                return False, None, f"Fila {fila_num + 2}: ISBN '{isbn}' ya está registrado"
        
        # Limpiar y normalizar datos
        datos_limpios = {
            'titulo': titulo,
            'autor_nombre': autor_nombre.title(),
            'autor_apellido': autor_apellido.title(),
            'isbn': isbn,
            'editorial': self._limpiar_texto(datos.get('editorial')),
            'fecha_publicacion': self._normalizar_fecha(datos.get('fecha_publicacion')),
            'numero_paginas': self._validar_numero(datos.get('numero_paginas')),
            'genero': self._limpiar_texto(datos.get('genero')),
            'cantidad_ejemplares': max(1, self._validar_numero(datos.get('cantidad_ejemplares'), default=1)),
        }
        
        return True, datos_limpios, None
    
    @transaction.atomic
    def importar(self, actualizar_existentes=False, crear_autores=True, crear_ejemplares=True):
        """
        Importa libros desde el archivo Excel.
        
        Args:
            actualizar_existentes: Si True, actualiza libros existentes (por ISBN)
            crear_autores: Si True, crea autores automáticamente si no existen
            crear_ejemplares: Si True, crea ejemplares según cantidad_ejemplares
        
        Returns:
            dict con resultados de la importación
        """
        try:
            # Leer el archivo Excel
            df = pd.read_excel(self.archivo_excel, engine='openpyxl')
            self.resultados['total_filas'] = len(df)
            
            # Normalizar nombres de columnas
            df.columns = df.columns.str.strip().str.lower()
            # Mapear variaciones de nombres de columnas
            mapeo_columnas = {
                'autor': 'autor_nombre',  # Si solo hay una columna "autor"
                'nombre_autor': 'autor_nombre',
                'nombre autor': 'autor_nombre',
                'apellido_autor': 'autor_apellido',
                'apellido autor': 'autor_apellido',
                'año': 'fecha_publicacion',
                'año_publicacion': 'fecha_publicacion',
                'paginas': 'numero_paginas',
                'numero_paginas': 'numero_paginas',
                'cantidad': 'cantidad_ejemplares',
                'ejemplares': 'cantidad_ejemplares',
            }
            
            for col_antigua, col_nueva in mapeo_columnas.items():
                if col_antigua in df.columns and col_nueva not in df.columns:
                    df[col_nueva] = df[col_antigua]
            
            # Validar columnas requeridas
            columnas_faltantes = [col for col in self.COLUMNAS_REQUERIDAS if col not in df.columns]
            if columnas_faltantes:
                raise ValueError(f"Columnas requeridas faltantes: {', '.join(columnas_faltantes)}")
            
            # Obtener libros existentes por ISBN para validación rápida
            isbns_existentes = set(
                Libro.objects.exclude(isbn__isnull=True).exclude(isbn='').values_list('isbn', flat=True)
            )
            
            # Procesar fila por fila
            libros_a_crear = []
            libros_a_actualizar = []
            libros_con_cantidad = {}  # {(titulo, autor_id, isbn): cantidad} para nuevos libros
            
            for idx, fila in df.iterrows():
                # Validar fila
                es_valida, datos_limpios, error = self._validar_fila(idx, fila)
                
                if not es_valida:
                    self.resultados['errores'].append(error)
                    self.resultados['omitidos'] += 1
                    continue
                
                # Obtener o crear autor
                if crear_autores:
                    autor = self._obtener_o_crear_autor(
                        datos_limpios['autor_nombre'],
                        datos_limpios['autor_apellido']
                    )
                else:
                    autor = Autor.objects.filter(
                        nombre__iexact=datos_limpios['autor_nombre'],
                        apellido__iexact=datos_limpios['autor_apellido']
                    ).first()
                    
                    if not autor:
                        self.resultados['errores'].append(
                            f"Fila {idx + 2}: Autor '{datos_limpios['autor_nombre']} {datos_limpios['autor_apellido']}' no existe"
                        )
                        self.resultados['omitidos'] += 1
                        continue
                
                # Preparar datos del libro (sin autor_nombre y autor_apellido)
                datos_libro = {
                    'titulo': datos_limpios['titulo'],
                    'autor': autor,
                    'isbn': datos_limpios['isbn'],
                    'editorial': datos_limpios['editorial'],
                    'fecha_publicacion': datos_limpios['fecha_publicacion'],
                    'numero_paginas': datos_limpios['numero_paginas'],
                    'genero': datos_limpios['genero'],
                }
                
                cantidad_ejemplares = datos_limpios['cantidad_ejemplares']
                
                # Buscar libro existente por ISBN
                libro_existente = None
                if datos_limpios['isbn'] and datos_limpios['isbn'] in isbns_existentes:
                    libro_existente = Libro.objects.filter(isbn=datos_limpios['isbn']).first()
                
                if libro_existente:
                    if actualizar_existentes:
                        # Actualizar libro existente
                        for campo, valor in datos_libro.items():
                            if campo != 'autor':  # No actualizar autor
                                setattr(libro_existente, campo, valor)
                        libro_existente.save()
                        libros_a_actualizar.append(libro_existente)
                        self.resultados['actualizados'] += 1
                        
                        # Crear ejemplares adicionales si se solicita
                        if crear_ejemplares and cantidad_ejemplares > 0:
                            ejemplares_existentes = libro_existente.ejemplares.count()
                            cantidad_a_crear = max(0, cantidad_ejemplares - ejemplares_existentes)
                            if cantidad_a_crear > 0:
                                self._crear_ejemplares(libro_existente, cantidad_a_crear)
                    else:
                        self.resultados['omitidos'] += 1
                        self.resultados['errores'].append(
                            f"Fila {idx + 2}: Libro con ISBN '{datos_limpios['isbn']}' ya existe"
                        )
                else:
                    # Crear nuevo libro
                    nuevo_libro = Libro(**datos_libro)
                    libros_a_crear.append(nuevo_libro)
                    self.resultados['importados'] += 1
                    
                    # Guardar cantidad de ejemplares para después de crear
                    key = (datos_limpios['titulo'], autor.id, datos_limpios['isbn'] or '')
                    libros_con_cantidad[key] = cantidad_ejemplares
                    
                    if datos_limpios['isbn']:
                        isbns_existentes.add(datos_limpios['isbn'])
            
            # Bulk create para nuevos libros
            if libros_a_crear:
                libros_creados = Libro.objects.bulk_create(libros_a_crear, ignore_conflicts=False)
                
                # Crear ejemplares para los nuevos libros
                if crear_ejemplares:
                    for libro_creado in libros_creados:
                        key = (libro_creado.titulo, libro_creado.autor.id, libro_creado.isbn or '')
                        cantidad = libros_con_cantidad.get(key, 1)
                        if cantidad > 0:
                            self._crear_ejemplares(libro_creado, cantidad)
            
            return self.resultados
            
        except Exception as e:
            self.resultados['errores'].append(f"Error general: {str(e)}")
            raise


def importar_libros_desde_excel(archivo_excel, actualizar_existentes=False, crear_autores=True, crear_ejemplares=True):
    """
    Función helper para importar libros desde Excel.
    
    Args:
        archivo_excel: Archivo Excel o ruta al archivo
        actualizar_existentes: Si True, actualiza libros existentes
        crear_autores: Si True, crea autores automáticamente
        crear_ejemplares: Si True, crea ejemplares
    
    Returns:
        dict con resultados de la importación
    """
    importer = LibrosImporter(archivo_excel)
    return importer.importar(
        actualizar_existentes=actualizar_existentes,
        crear_autores=crear_autores,
        crear_ejemplares=crear_ejemplares
    )

