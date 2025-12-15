"""
Servicios de lógica de negocio para libros.
"""
from django.db.models import Count, Q


class LibroService:
    """Servicio para operaciones de libros."""
    
    @staticmethod
    def buscar_libros_optimizado(queryset=None, titulo=None, autor=None, genero=None):
        """
        Busca libros de forma optimizada usando annotate para evitar Query N+1.
        
        Args:
            queryset: QuerySet inicial (opcional)
            titulo: Filtro por título
            autor: Filtro por autor (nombre o apellido)
            genero: Filtro por género
        
        Returns:
            QuerySet optimizado con ejemplares_disponibles y total_ejemplares
        """
        from .models import Libro
        
        if queryset is None:
            libros = Libro.objects.select_related('autor').all()
        else:
            libros = queryset
        
        if titulo:
            libros = libros.filter(titulo__icontains=titulo)
        
        if autor:
            libros = libros.filter(
                Q(autor__nombre__icontains=autor) | 
                Q(autor__apellido__icontains=autor)
            )
        
        if genero:
            libros = libros.filter(genero__icontains=genero)
        
        libros = libros.annotate(
            ejemplares_disponibles=Count(
                'ejemplares',
                filter=Q(ejemplares__estado='DISPONIBLE')
            ),
            total_ejemplares=Count('ejemplares')
        )
        
        return libros
    
    @staticmethod
    def obtener_generos_disponibles():
        """
        Obtiene lista de géneros únicos disponibles.
        
        Returns:
            QuerySet con géneros únicos
        """
        from .models import Libro
        return Libro.objects.exclude(
            genero__isnull=True
        ).exclude(
            genero=''
        ).values_list('genero', flat=True).distinct()
