from django.contrib import admin
from .models import Prestamo, Reserva


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('ejemplar', 'socio', 'fecha_prestamo', 'fecha_devolucion_esperada', 'fecha_devolucion_real', 'estado')
    list_filter = ('estado', 'fecha_prestamo', 'fecha_devolucion_esperada')
    search_fields = ('ejemplar__libro__titulo', 'ejemplar__codigo', 'socio__nombre', 'socio__apellido', 'socio__identificacion')
    ordering = ('-fecha_prestamo',)
    date_hierarchy = 'fecha_prestamo'
    readonly_fields = ('fecha_prestamo',)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('libro', 'socio', 'fecha_reserva', 'estado')
    list_filter = ('estado', 'fecha_reserva')
    search_fields = ('libro__titulo', 'socio__nombre', 'socio__apellido')
    ordering = ('-fecha_reserva',)
    date_hierarchy = 'fecha_reserva'
