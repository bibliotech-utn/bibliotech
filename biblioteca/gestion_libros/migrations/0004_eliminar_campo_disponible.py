# Generated manually - Remove unused 'disponible' field

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_libros', '0003_ejemplar'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='libro',
            name='disponible',
        ),
    ]
