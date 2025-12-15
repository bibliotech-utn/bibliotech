from django.db import models
from django.utils import timezone
from gestion_socios.models import Socio
from gestion_libros.models import Ejemplar, Libro

class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('NOTIFICADA', 'Notificada'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='reservas', db_index=True)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='reservas', db_index=True)
    fecha_reserva = models.DateTimeField(auto_now_add=True, db_index=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE',
        db_index=True
    )
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.libro.titulo} - {self.socio.nombre} {self.socio.apellido} ({self.estado})"

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-fecha_reserva']
        indexes = [
            models.Index(fields=['socio', 'estado']),
            models.Index(fields=['libro', 'estado']),
        ]

class Prestamo(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('DEVUELTO', 'Devuelto'),
        ('VENCIDO', 'Vencido'),
    ]
    
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='prestamos', db_index=True)
    ejemplar = models.ForeignKey(Ejemplar, on_delete=models.CASCADE, related_name='prestamos', db_index=True)
    fecha_prestamo = models.DateField(auto_now_add=True, db_index=True)
    fecha_devolucion_esperada = models.DateField(db_index=True)
    fecha_devolucion_real = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE', db_index=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.ejemplar.libro.titulo} - {self.socio.nombre} {self.socio.apellido} ({self.estado})"

    def calcular_dias_atraso(self):
        """Calcula los días de atraso si el préstamo está vencido"""
        if self.estado == 'PENDIENTE' and self.fecha_devolucion_esperada < timezone.now().date():
            dias = (timezone.now().date() - self.fecha_devolucion_esperada).days
            return dias
        return 0
    
    def actualizar_estado_vencido(self):
        """Actualiza el estado a VENCIDO si está pendiente y vencido"""
        if self.estado == 'PENDIENTE' and self.fecha_devolucion_esperada < timezone.now().date():
            self.estado = 'VENCIDO'
            self.save(update_fields=['estado'])

    def marcar_como_devuelto(self):
        """
        Marca el préstamo como devuelto y actualiza el ejemplar.
        Usa transacción atómica para garantizar consistencia.
        """
        from django.db import transaction
        with transaction.atomic():
            self.estado = 'DEVUELTO'
            self.fecha_devolucion_real = timezone.now().date()
            self.ejemplar.estado = 'DISPONIBLE'
            self.ejemplar.save(update_fields=['estado'])
            self.save(update_fields=['estado', 'fecha_devolucion_real'])
    
    @classmethod
    def actualizar_estados_vencidos(cls):
        """Actualiza todos los préstamos vencidos a estado VENCIDO"""
        vencidos = cls.objects.filter(
            estado='PENDIENTE',
            fecha_devolucion_esperada__lt=timezone.now().date()
        )
        count = vencidos.update(estado='VENCIDO')
        return count

    class Meta:
        verbose_name = "Préstamo"
        verbose_name_plural = "Préstamos"
        ordering = ['-fecha_prestamo']