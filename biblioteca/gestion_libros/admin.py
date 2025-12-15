from django.contrib import admin
from .models import Libro, Ejemplar


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'editorial', 'isbn', 'fecha_registro')
    list_filter = ('fecha_publicacion', 'editorial', 'autor', 'genero')
    search_fields = ('titulo', 'isbn', 'editorial', 'autor__nombre', 'autor__apellido')
    ordering = ('titulo',)
    date_hierarchy = 'fecha_registro'


@admin.register(Ejemplar)
class EjemplarAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'libro', 'estado', 'ubicacion')
    list_filter = ('estado',)
    search_fields = ('codigo', 'libro__titulo')
    ordering = ('libro', 'codigo')
