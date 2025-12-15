from django.contrib import admin
from .models import Socio


@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'identificacion', 'email', 'activo', 'fecha_registro')
    list_filter = ('activo', 'fecha_registro')
    search_fields = ('nombre', 'apellido', 'identificacion', 'email')
    ordering = ('apellido', 'nombre')
