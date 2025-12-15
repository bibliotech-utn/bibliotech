"""
Modelo para el historial de importaciones desde Excel.
"""
from django.db import models
from django.contrib.auth.models import User


class HistorialImportacion(models.Model):
    """
    Modelo para registrar el historial de importaciones desde Excel.
    """
    TIPO_CHOICES = [
        ('autores', 'Autores'),
        ('libros', 'Libros'),
        ('socios', 'Socios'),
    ]
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        db_index=True
    )
    archivo = models.FileField(
        upload_to='importaciones/%Y/%m/%d/',
        help_text="Archivo Excel subido"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Usuario que realizó la importación"
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    registros_importados = models.IntegerField(
        default=0,
        help_text="Cantidad de registros importados exitosamente"
    )
    registros_actualizados = models.IntegerField(
        default=0,
        help_text="Cantidad de registros actualizados"
    )
    registros_omitidos = models.IntegerField(
        default=0,
        help_text="Cantidad de registros omitidos"
    )
    total_filas = models.IntegerField(
        default=0,
        help_text="Total de filas procesadas"
    )
    errores = models.IntegerField(
        default=0,
        help_text="Cantidad de errores encontrados"
    )
    detalles_adicionales = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detalles adicionales (ej: ejemplares creados, autores creados)"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text="Observaciones sobre la importación"
    )
    
    class Meta:
        verbose_name = "Historial de Importación"
        verbose_name_plural = "Historial de Importaciones"
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.fecha.strftime('%d/%m/%Y %H:%M')} - {self.registros_importados} importados"

