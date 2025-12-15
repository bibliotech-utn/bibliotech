from django.contrib import admin
from .models import HistorialImportacion


@admin.register(HistorialImportacion)
class HistorialImportacionAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'fecha', 'usuario', 'registros_importados', 'registros_actualizados', 'errores', 'total_filas']
    list_filter = ['tipo', 'fecha', 'usuario']
    search_fields = ['tipo', 'observaciones']
    readonly_fields = ['fecha']
    date_hierarchy = 'fecha'

