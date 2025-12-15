from django.contrib import admin
from .models import Personal


@admin.register(Personal)
class PersonalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'cargo', 'activo', 'fecha_registro')
    list_filter = ('activo', 'cargo', 'fecha_registro')
    search_fields = ('nombre', 'apellido', 'user__username')
    ordering = ('apellido', 'nombre')
