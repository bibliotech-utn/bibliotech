"""
Módulo de importación de autores desde archivos Excel.
Permite importar grandes volúmenes de autores de forma optimizada.
"""
import pandas as pd
from datetime import datetime
from django.db import transaction
from django.core.exceptions import ValidationError
from gestion_autores.models import Autor


class AutoresImporter:
    """
    Clase para importar autores desde archivos Excel.
    
    Columnas esperadas en el Excel:
    - nombre (requerido)
    - apellido (requerido)
    - nacionalidad (opcional)
    - fecha_nacimiento (opcional, formato: YYYY-MM-DD o DD/MM/YYYY)
    - biografia (opcional)
    """
    
    COLUMNAS_REQUERIDAS = ['nombre', 'apellido']
    COLUMNAS_OPCIONALES = ['nacionalidad', 'fecha_nacimiento', 'biografia']
    
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
            'errores': []
        }
    
    def _normalizar_fecha(self, valor):
        """
        Normaliza diferentes formatos de fecha a objeto date.
        
        Args:
            valor: Valor de fecha (puede ser string, datetime, o date)
        
        Returns:
            date o None
        """
        if pd.isna(valor) or valor is None or valor == '':
            return None
        
        # Si ya es un objeto date o datetime
        if isinstance(valor, (datetime, pd.Timestamp)):
            return valor.date() if hasattr(valor, 'date') else valor
        
        # Si es string, intentar parsear
        if isinstance(valor, str):
            valor = valor.strip()
            if not valor:
                return None
            
            # Intentar diferentes formatos
            formatos = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
            for formato in formatos:
                try:
                    return datetime.strptime(valor, formato).date()
                except ValueError:
                    continue
            
            # Si pandas puede parsearlo
            try:
                return pd.to_datetime(valor).date()
            except:
                pass
        
        return None
    
    def _limpiar_texto(self, valor):
        """
        Limpia y normaliza texto.
        
        Args:
            valor: Valor a limpiar
        
        Returns:
            str limpio o None
        """
        if pd.isna(valor) or valor is None:
            return None
        
        texto = str(valor).strip()
        return texto if texto else None
    
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
        nombre = self._limpiar_texto(datos.get('nombre'))
        apellido = self._limpiar_texto(datos.get('apellido'))
        
        if not nombre:
            errores.append("Nombre es requerido")
        if not apellido:
            errores.append("Apellido es requerido")
        
        if errores:
            return False, None, f"Fila {fila_num + 2}: {', '.join(errores)}"
        
        # Limpiar y normalizar datos
        datos_limpios = {
            'nombre': nombre.title(),
            'apellido': apellido.title(),
            'nacionalidad': self._limpiar_texto(datos.get('nacionalidad')),
            'fecha_nacimiento': self._normalizar_fecha(datos.get('fecha_nacimiento')),
            'biografia': self._limpiar_texto(datos.get('biografia')),
        }
        
        return True, datos_limpios, None
    
    @transaction.atomic
    def importar(self, actualizar_existentes=False):
        """
        Importa autores desde el archivo Excel.
        
        Args:
            actualizar_existentes: Si True, actualiza autores existentes (mismo nombre y apellido)
        
        Returns:
            dict con resultados de la importación
        """
        try:
            # Leer el archivo Excel
            df = pd.read_excel(self.archivo_excel, engine='openpyxl')
            self.resultados['total_filas'] = len(df)
            
            # Normalizar nombres de columnas (minúsculas, sin espacios)
            df.columns = df.columns.str.strip().str.lower()
            
            # Validar que existan las columnas requeridas
            columnas_faltantes = [col for col in self.COLUMNAS_REQUERIDAS if col not in df.columns]
            if columnas_faltantes:
                raise ValueError(f"Columnas requeridas faltantes: {', '.join(columnas_faltantes)}")
            
            # Procesar fila por fila
            autores_a_crear = []
            autores_a_actualizar = []
            
            for idx, fila in df.iterrows():
                # Validar fila
                es_valida, datos_limpios, error = self._validar_fila(idx, fila)
                
                if not es_valida:
                    self.resultados['errores'].append(error)
                    self.resultados['omitidos'] += 1
                    continue
                
                # Buscar autor existente por nombre y apellido
                autor_existente = Autor.objects.filter(
                    nombre__iexact=datos_limpios['nombre'],
                    apellido__iexact=datos_limpios['apellido']
                ).first()
                
                if autor_existente:
                    if actualizar_existentes:
                        # Actualizar autor existente
                        for campo, valor in datos_limpios.items():
                            if valor is not None:
                                setattr(autor_existente, campo, valor)
                        autores_a_actualizar.append(autor_existente)
                        self.resultados['actualizados'] += 1
                    else:
                        self.resultados['omitidos'] += 1
                        self.resultados['errores'].append(
                            f"Fila {idx + 2}: Autor '{datos_limpios['nombre']} {datos_limpios['apellido']}' ya existe"
                        )
                else:
                    # Crear nuevo autor
                    autores_a_crear.append(Autor(**datos_limpios))
                    self.resultados['importados'] += 1
            
            # Bulk create para nuevos autores (optimizado)
            if autores_a_crear:
                Autor.objects.bulk_create(autores_a_crear, ignore_conflicts=False)
            
            # Bulk update para autores existentes
            if autores_a_actualizar:
                campos_update = ['nombre', 'apellido', 'nacionalidad', 'fecha_nacimiento', 'biografia']
                Autor.objects.bulk_update(autores_a_actualizar, campos_update)
            
            return self.resultados
            
        except Exception as e:
            self.resultados['errores'].append(f"Error general: {str(e)}")
            raise


def importar_autores_desde_excel(archivo_excel, actualizar_existentes=False):
    """
    Función helper para importar autores desde Excel.
    
    Args:
        archivo_excel: Archivo Excel o ruta al archivo
        actualizar_existentes: Si True, actualiza autores existentes
    
    Returns:
        dict con resultados de la importación
    """
    importer = AutoresImporter(archivo_excel)
    return importer.importar(actualizar_existentes=actualizar_existentes)

