"""
Servicios de lógica de negocio para préstamos.
"""
from django.utils import timezone
from django.db import transaction
from .models import Prestamo


class PrestamoService:
    """Servicio para operaciones de préstamos."""
    
    @staticmethod
    def validar_limite_prestamos(socio, limite=3):
        """
        Valida si un socio puede solicitar más préstamos.
        
        Args:
            socio: Instancia de Socio
            limite: Límite máximo de préstamos simultáneos (default: 3)
        
        Returns:
            Tuple (puede_prestar: bool, mensaje_error: str o None)
        """
        prestamos_activos = Prestamo.objects.filter(
            socio=socio,
            estado='PENDIENTE'
        ).count()
        
        if prestamos_activos >= limite:
            return False, f'Has alcanzado el límite de préstamos simultáneos ({limite})'
        
        prestamos_vencidos = Prestamo.objects.filter(
            socio=socio,
            estado='PENDIENTE',
            fecha_devolucion_esperada__lt=timezone.now().date()
        ).exists()
        
        if prestamos_vencidos:
            return False, 'Tienes préstamos vencidos. Debes devolverlos antes de solicitar uno nuevo.'
        
        return True, None
    
    @staticmethod
    @transaction.atomic
    def crear_prestamo_seguro(socio, ejemplar, fecha_devolucion_esperada):
        """
        Crea un préstamo de forma segura con transacción atómica.
        
        Args:
            socio: Instancia de Socio
            ejemplar: Instancia de Ejemplar
            fecha_devolucion_esperada: Fecha de devolución esperada
        
        Returns:
            Prestamo creado
        
        Raises:
            ValueError: Si el ejemplar no está disponible
        """
        import logging
        from gestion_prestamos.models import Prestamo
        
        logger = logging.getLogger('gestion_prestamos')
        
        ejemplar_disponible = ejemplar.__class__.objects.select_for_update().filter(
            id=ejemplar.id,
            estado='DISPONIBLE'
        ).first()
        
        if not ejemplar_disponible:
            logger.warning(f'Intento de préstamo de ejemplar no disponible: {ejemplar.id}')
            raise ValueError('El ejemplar no está disponible')
        
        prestamo_pendiente = Prestamo.objects.filter(
            ejemplar=ejemplar_disponible,
            estado='PENDIENTE'
        ).exists()
        
        if prestamo_pendiente:
            logger.warning(f'Intento de préstamo de ejemplar con préstamo pendiente: {ejemplar.id}')
            raise ValueError('El ejemplar ya tiene un préstamo pendiente')
        
        prestamo = Prestamo.objects.create(
            socio=socio,
            ejemplar=ejemplar_disponible,
            fecha_devolucion_esperada=fecha_devolucion_esperada,
            estado='PENDIENTE'
        )
        
        ejemplar_disponible.estado = 'PRESTADO'
        ejemplar_disponible.save(update_fields=['estado'])
        
        logger.info(f'Préstamo creado: ID={prestamo.id}, Socio={socio.id}, Ejemplar={ejemplar_disponible.id}')
        
        return prestamo
    
    @staticmethod
    def actualizar_estados_vencidos():
        """
        Actualiza todos los préstamos vencidos a estado VENCIDO.
        
        Returns:
            Número de préstamos actualizados
        """
        vencidos = Prestamo.objects.filter(
            estado='PENDIENTE',
            fecha_devolucion_esperada__lt=timezone.now().date()
        )
        count = vencidos.update(estado='VENCIDO')
        return count
