from django.db import models
from django.contrib.auth.models import User


class Socio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    identificacion = models.CharField(
        max_length=15,
        unique=True,
        db_index=True,
        help_text="DNI, Cédula o ID de Socio"
    )
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True, db_index=True)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.identificacion})"