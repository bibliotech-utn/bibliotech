from django.contrib import admin
from .models import Autor


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'nacionalidad', 'fecha_nacimiento', 'fecha_registro')
    list_filter = ('nacionalidad', 'fecha_registro')
    search_fields = ('nombre', 'apellido', 'nacionalidad')
    ordering = ('apellido', 'nombre')
