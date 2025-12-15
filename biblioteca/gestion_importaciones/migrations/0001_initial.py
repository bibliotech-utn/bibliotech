# Generated manually
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HistorialImportacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('autores', 'Autores'), ('libros', 'Libros'), ('socios', 'Socios')], db_index=True, max_length=20)),
                ('archivo', models.FileField(help_text='Archivo Excel subido', upload_to='importaciones/%Y/%m/%d/')),
                ('fecha', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('registros_importados', models.IntegerField(default=0, help_text='Cantidad de registros importados exitosamente')),
                ('registros_actualizados', models.IntegerField(default=0, help_text='Cantidad de registros actualizados')),
                ('registros_omitidos', models.IntegerField(default=0, help_text='Cantidad de registros omitidos')),
                ('total_filas', models.IntegerField(default=0, help_text='Total de filas procesadas')),
                ('errores', models.IntegerField(default=0, help_text='Cantidad de errores encontrados')),
                ('detalles_adicionales', models.JSONField(blank=True, default=dict, help_text='Detalles adicionales (ej: ejemplares creados, autores creados)')),
                ('observaciones', models.TextField(blank=True, help_text='Observaciones sobre la importación', null=True)),
                ('usuario', models.ForeignKey(blank=True, help_text='Usuario que realizó la importación', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Historial de Importación',
                'verbose_name_plural': 'Historial de Importaciones',
                'ordering': ['-fecha'],
            },
        ),
    ]

