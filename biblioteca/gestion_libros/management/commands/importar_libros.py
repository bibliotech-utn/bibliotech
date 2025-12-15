"""
Comando de Django para importar libros desde un archivo Excel.
Uso: python manage.py importar_libros archivo.xlsx [--actualizar] [--no-crear-autores] [--no-crear-ejemplares]
"""
from django.core.management.base import BaseCommand, CommandError
from gestion_libros.importadores.libros_importer import importar_libros_desde_excel
import os


class Command(BaseCommand):
    help = 'Importa libros desde un archivo Excel (.xlsx)'

    def add_arguments(self, parser):
        parser.add_argument(
            'archivo',
            type=str,
            help='Ruta al archivo Excel (.xlsx)'
        )
        parser.add_argument(
            '--actualizar',
            action='store_true',
            help='Actualizar libros existentes (mismo ISBN)',
        )
        parser.add_argument(
            '--no-crear-autores',
            action='store_true',
            help='No crear autores automáticamente si no existen',
        )
        parser.add_argument(
            '--no-crear-ejemplares',
            action='store_true',
            help='No crear ejemplares automáticamente',
        )

    def handle(self, *args, **options):
        archivo = options['archivo']
        actualizar_existentes = options.get('actualizar', False)
        crear_autores = not options.get('no_crear_autores', False)
        crear_ejemplares = not options.get('no_crear_ejemplares', False)

        # Validar que el archivo exista
        if not os.path.exists(archivo):
            raise CommandError(f'El archivo "{archivo}" no existe.')

        if not archivo.endswith(('.xlsx', '.xls')):
            raise CommandError('El archivo debe ser un Excel (.xlsx o .xls)')

        self.stdout.write(self.style.SUCCESS(f'Importando libros desde: {archivo}'))
        self.stdout.write(f'Opciones: crear_autores={crear_autores}, crear_ejemplares={crear_ejemplares}, actualizar={actualizar_existentes}')
        self.stdout.write('')

        try:
            # Importar libros
            resultados = importar_libros_desde_excel(
                archivo,
                actualizar_existentes=actualizar_existentes,
                crear_autores=crear_autores,
                crear_ejemplares=crear_ejemplares
            )

            # Mostrar resultados
            self.stdout.write(self.style.SUCCESS('=' * 50))
            self.stdout.write(self.style.SUCCESS('RESULTADOS DE LA IMPORTACIÓN'))
            self.stdout.write(self.style.SUCCESS('=' * 50))
            self.stdout.write(f'Total de filas procesadas: {resultados["total_filas"]}')
            self.stdout.write(self.style.SUCCESS(f'✓ Libros importados: {resultados["importados"]}'))
            self.stdout.write(self.style.WARNING(f'⚠ Libros actualizados: {resultados["actualizados"]}'))
            self.stdout.write(self.style.WARNING(f'⚠ Libros omitidos: {resultados["omitidos"]}'))
            self.stdout.write(self.style.SUCCESS(f'✓ Ejemplares creados: {resultados["ejemplares_creados"]}'))
            self.stdout.write(self.style.SUCCESS(f'✓ Autores creados: {resultados["autores_creados"]}'))

            if resultados['errores']:
                self.stdout.write(self.style.ERROR(f'\n✗ Errores encontrados: {len(resultados["errores"])}'))
                self.stdout.write('')
                self.stdout.write(self.style.ERROR('PRIMEROS 20 ERRORES:'))
                for error in resultados['errores'][:20]:
                    self.stdout.write(self.style.ERROR(f'  - {error}'))
                
                if len(resultados['errores']) > 20:
                    self.stdout.write(self.style.ERROR(f'  ... y {len(resultados["errores"]) - 20} errores más'))
            else:
                self.stdout.write(self.style.SUCCESS('\n✓ No se encontraron errores'))

            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('Importación completada exitosamente.'))

        except Exception as e:
            raise CommandError(f'Error al importar: {str(e)}')

