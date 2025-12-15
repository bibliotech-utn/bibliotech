from django.db import models
from gestion_autores.models import Autor


class Libro(models.Model):
    titulo = models.CharField(max_length=200, db_index=True)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name='libros', db_index=True)
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True, help_text="ISBN-13 (13 caracteres)")
    editorial = models.CharField(max_length=100, blank=True, null=True)
    fecha_publicacion = models.DateField(blank=True, null=True)
    numero_paginas = models.IntegerField(blank=True, null=True)
    genero = models.CharField(max_length=100, blank=True, null=True, help_text="Género literario del libro")
    fecha_registro = models.DateField(auto_now_add=True)
    
    @property
    def tiene_ejemplares_disponibles(self):
        """Verifica si el libro tiene ejemplares disponibles"""
        return self.ejemplares.filter(estado='DISPONIBLE').exists()

    def __str__(self):
        return f"{self.titulo} - {self.autor}"

    class Meta:
        verbose_name = "Libro"
        verbose_name_plural = "Libros"
        ordering = ['titulo']


class Ejemplar(models.Model):
    ESTADO_CHOICES = [
        ("DISPONIBLE", "Disponible"),
        ("PRESTADO", "Prestado"),
        ("REPARACION", "En reparación"),
        ("PERDIDO", "Perdido"),
    ]
    
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name="ejemplares", db_index=True)
    codigo = models.CharField(max_length=50, unique=True, db_index=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="DISPONIBLE",
        db_index=True
    )
    ubicacion = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.libro.titulo} - {self.codigo} ({self.estado})"

    class Meta:
        verbose_name = "Ejemplar"
        verbose_name_plural = "Ejemplares"
        ordering = ['libro', 'codigo']