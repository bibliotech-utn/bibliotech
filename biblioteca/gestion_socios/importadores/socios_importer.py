"""
Módulo de importación de socios desde archivos Excel.
Permite importar grandes volúmenes de socios de forma optimizada.
"""
import pandas as pd
from datetime import datetime
from django.db import transaction
from django.contrib.auth.models import User
from gestion_socios.models import Socio


class SociosImporter:
    """
    Clase para importar socios desde archivos Excel.
    
    Columnas esperadas en el Excel:
    - nombre (requerido)
    - apellido (requerido)
    - identificacion (requerido, único)
    - email (requerido, único)
    - telefono (opcional)
    - activo (opcional, True/False, default: True)
    """
    
    COLUMNAS_REQUERIDAS = ['nombre', 'apellido', 'identificacion', 'email']
    COLUMNAS_OPCIONALES = ['telefono', 'activo']
    
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
    
    def _limpiar_texto(self, valor):
        """Limpia y normaliza texto."""
        if pd.isna(valor) or valor is None:
            return None
        texto = str(valor).strip()
        return texto if texto else None
    
    def _limpiar_email(self, valor):
        """Limpia y normaliza email."""
        email = self._limpiar_texto(valor)
        if email:
            email = email.lower()
        return email
    
    def _validar_boolean(self, valor):
        """Convierte valor a boolean."""
        if pd.isna(valor) or valor is None:
            return True  # Default activo=True
        
        if isinstance(valor, bool):
            return valor
        
        valor_str = str(valor).strip().lower()
        return valor_str in ['true', '1', 'si', 'sí', 'yes', 'verdadero', 'activo']
    
    def _validar_email(self, email):
        """Valida formato de email."""
        if not email:
            return False, "Email es requerido"
        
        if '@' not in email or '.' not in email.split('@')[-1]:
            return False, "Formato de email inválido"
        
        return True, None
    
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
        identificacion = self._limpiar_texto(datos.get('identificacion'))
        email = self._limpiar_email(datos.get('email'))
        
        if not nombre:
            errores.append("Nombre es requerido")
        if not apellido:
            errores.append("Apellido es requerido")
        if not identificacion:
            errores.append("Identificación es requerida")
        if not email:
            errores.append("Email es requerido")
        
        # Validar email
        if email:
            es_valido, error_email = self._validar_email(email)
            if not es_valido:
                errores.append(error_email)
        
        if errores:
            return False, None, f"Fila {fila_num + 2}: {', '.join(errores)}"
        
        # Limpiar y normalizar datos
        datos_limpios = {
            'nombre': nombre.title(),
            'apellido': apellido.title(),
            'identificacion': identificacion,
            'email': email,
            'telefono': self._limpiar_texto(datos.get('telefono')),
            'activo': self._validar_boolean(datos.get('activo')),
        }
        
        return True, datos_limpios, None
    
    def _crear_usuario_para_socio(self, socio):
        """
        Crea un usuario de Django para el socio si no existe.
        
        Args:
            socio: Instancia de Socio
        """
        if socio.user:
            return  # Ya tiene usuario
        
        # Generar username único
        username_base = f"{socio.email.split('@')[0]}_{socio.identificacion}"
        username = username_base
        contador = 1
        
        while User.objects.filter(username=username).exists():
            username = f"{username_base}_{contador}"
            contador += 1
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=socio.email,
            password='temporal123',  # Password temporal, el socio deberá cambiarla
            first_name=socio.nombre,
            last_name=socio.apellido,
            is_active=socio.activo
        )
        
        socio.user = user
        socio.save(update_fields=['user'])
    
    @transaction.atomic
    def importar(self, actualizar_existentes=False, crear_usuarios=False):
        """
        Importa socios desde el archivo Excel.
        
        Args:
            actualizar_existentes: Si True, actualiza socios existentes
            crear_usuarios: Si True, crea usuarios de Django para los socios
        
        Returns:
            dict con resultados de la importación
        """
        try:
            # Leer el archivo Excel
            df = pd.read_excel(self.archivo_excel, engine='openpyxl')
            self.resultados['total_filas'] = len(df)
            
            # Normalizar nombres de columnas
            df.columns = df.columns.str.strip().str.lower()
            
            # Validar columnas requeridas
            columnas_faltantes = [col for col in self.COLUMNAS_REQUERIDAS if col not in df.columns]
            if columnas_faltantes:
                raise ValueError(f"Columnas requeridas faltantes: {', '.join(columnas_faltantes)}")
            
            # Obtener socios existentes para validación rápida
            identificaciones_existentes = set(
                Socio.objects.values_list('identificacion', flat=True)
            )
            emails_existentes = set(
                Socio.objects.values_list('email', flat=True)
            )
            
            # Procesar fila por fila
            socios_a_crear = []
            socios_a_actualizar = []
            
            for idx, fila in df.iterrows():
                # Validar fila
                es_valida, datos_limpios, error = self._validar_fila(idx, fila)
                
                if not es_valida:
                    self.resultados['errores'].append(error)
                    self.resultados['omitidos'] += 1
                    continue
                
                # Verificar duplicados
                identificacion = datos_limpios['identificacion']
                email = datos_limpios['email']
                
                # Buscar por identificación o email
                socio_existente = None
                if identificacion in identificaciones_existentes:
                    socio_existente = Socio.objects.filter(identificacion=identificacion).first()
                elif email in emails_existentes:
                    socio_existente = Socio.objects.filter(email=email).first()
                
                if socio_existente:
                    if actualizar_existentes:
                        # Actualizar socio existente
                        for campo, valor in datos_limpios.items():
                            if campo != 'identificacion':  # No actualizar identificación
                                setattr(socio_existente, campo, valor)
                        socios_a_actualizar.append(socio_existente)
                        self.resultados['actualizados'] += 1
                    else:
                        self.resultados['omitidos'] += 1
                        self.resultados['errores'].append(
                            f"Fila {idx + 2}: Socio con identificación '{identificacion}' o email '{email}' ya existe"
                        )
                else:
                    # Crear nuevo socio
                    socios_a_crear.append(Socio(**datos_limpios))
                    self.resultados['importados'] += 1
                    identificaciones_existentes.add(identificacion)
                    emails_existentes.add(email)
            
            # Bulk create para nuevos socios
            if socios_a_crear:
                socios_creados = Socio.objects.bulk_create(socios_a_crear, ignore_conflicts=False)
                
                # Crear usuarios si se solicita
                if crear_usuarios:
                    for socio in socios_creados:
                        self._crear_usuario_para_socio(socio)
            
            # Bulk update para socios existentes
            if socios_a_actualizar:
                campos_update = ['nombre', 'apellido', 'email', 'telefono', 'activo']
                Socio.objects.bulk_update(socios_a_actualizar, campos_update)
            
            return self.resultados
            
        except Exception as e:
            self.resultados['errores'].append(f"Error general: {str(e)}")
            raise


def importar_socios_desde_excel(archivo_excel, actualizar_existentes=False, crear_usuarios=False):
    """
    Función helper para importar socios desde Excel.
    
    Args:
        archivo_excel: Archivo Excel o ruta al archivo
        actualizar_existentes: Si True, actualiza socios existentes
        crear_usuarios: Si True, crea usuarios de Django
    
    Returns:
        dict con resultados de la importación
    """
    importer = SociosImporter(archivo_excel)
    return importer.importar(actualizar_existentes=actualizar_existentes, crear_usuarios=crear_usuarios)

