"""
Comando de Django para importar socios desde un archivo Excel.
Uso: python manage.py importar_socios archivo.xlsx [--actualizar] [--crear-usuarios]
"""
from django.core.management.base import BaseCommand, CommandError
from gestion_socios.importadores.socios_importer import importar_socios_desde_excel
import os


class Command(BaseCommand):
    help = 'Importa socios desde un archivo Excel (.xlsx)'

    def add_arguments(self, parser):
        parser.add_argument(
            'archivo',
            type=str,
            help='Ruta al archivo Excel (.xlsx)'
        )
        parser.add_argument(
            '--actualizar',
            action='store_true',
            help='Actualizar socios existentes (misma identificación o email)',
        )
        parser.add_argument(
            '--crear-usuarios',
            action='store_true',
            help='Crear usuarios de Django para los socios (password temporal)',
        )

    def handle(self, *args, **options):
        archivo = options['archivo']
        actualizar_existentes = options.get('actualizar', False)
        crear_usuarios = options.get('crear_usuarios', False)

        # Validar que el archivo exista
        if not os.path.exists(archivo):
            raise CommandError(f'El archivo "{archivo}" no existe.')

        if not archivo.endswith(('.xlsx', '.xls')):
            raise CommandError('El archivo debe ser un Excel (.xlsx o .xls)')

        self.stdout.write(self.style.SUCCESS(f'Importando socios desde: {archivo}'))
        self.stdout.write(f'Opciones: actualizar={actualizar_existentes}, crear_usuarios={crear_usuarios}')
        self.stdout.write('')

        try:
            # Importar socios
            resultados = importar_socios_desde_excel(
                archivo,
                actualizar_existentes=actualizar_existentes,
                crear_usuarios=crear_usuarios
            )

            # Mostrar resultados
            self.stdout.write(self.style.SUCCESS('=' * 50))
            self.stdout.write(self.style.SUCCESS('RESULTADOS DE LA IMPORTACIÓN'))
            self.stdout.write(self.style.SUCCESS('=' * 50))
            self.stdout.write(f'Total de filas procesadas: {resultados["total_filas"]}')
            self.stdout.write(self.style.SUCCESS(f'✓ Socios importados: {resultados["importados"]}'))
            self.stdout.write(self.style.WARNING(f'⚠ Socios actualizados: {resultados["actualizados"]}'))
            self.stdout.write(self.style.WARNING(f'⚠ Socios omitidos: {resultados["omitidos"]}'))

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

