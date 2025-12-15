from django import forms
from .models import Libro
from gestion_autores.models import Autor

class LibroForm(forms.ModelForm):
    GENERO_CHOICES = [
        ('', 'Seleccione un género'),
        ('Romance', 'Romance'),
        ('Ciencia ficción', 'Ciencia ficción'),
        ('Policial', 'Policial'),
        ('Historia', 'Historia'),
        ('Economía', 'Economía'),
        ('Novela', 'Novela'),
        ('Autoayuda', 'Autoayuda'),
        ('Misterio', 'Misterio'),
        ('Drama', 'Drama'),
        ('Poesía', 'Poesía'),
        ('Finanzas', 'Finanzas'),
        ('Finanzas personales', 'Finanzas personales'),
        ('Aventuras', 'Aventuras'),
        ('Biografía', 'Biografía'),
    ]
    
    class Meta:
        model = Libro
        fields = ['titulo', 'autor', 'isbn', 'editorial', 'fecha_publicacion', 'numero_paginas', 'genero']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el título del libro'
            }),
            'autor': forms.Select(attrs={
                'class': 'form-control'
            }),
            'isbn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ISBN-13 (13 caracteres)',
                'maxlength': '13'
            }),
            'editorial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la editorial'
            }),
            'fecha_publicacion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'numero_paginas': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de páginas',
                'min': '1'
            }),
        }
        labels = {
            'titulo': 'Título',
            'autor': 'Autor',
            'isbn': 'ISBN',
            'editorial': 'Editorial',
            'fecha_publicacion': 'Fecha de Publicación',
            'numero_paginas': 'Número de Páginas',
            'genero': 'Género',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar género como ChoiceField
        genero_initial = ''
        if self.instance and self.instance.pk and self.instance.genero:
            genero_initial = self.instance.genero
        
        self.fields['genero'] = forms.ChoiceField(
            choices=self.GENERO_CHOICES,
            required=False,
            widget=forms.Select(attrs={'class': 'form-control'}),
            label='Género',
            initial=genero_initial
        )
        # Ordenar autores por apellido y nombre
        self.fields['autor'].queryset = Autor.objects.all().order_by('apellido', 'nombre')
        # Agregar opción vacía si no hay autores
        if not Autor.objects.exists():
            self.fields['autor'].widget.attrs['disabled'] = True
            self.fields['autor'].help_text = 'Primero debe crear al menos un autor'

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        if titulo:
            titulo = titulo.strip()
        return titulo

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        if isbn:
            isbn = isbn.strip().replace('-', '').replace(' ', '')
            if len(isbn) != 13 and len(isbn) != 10:
                raise forms.ValidationError('El ISBN debe tener 10 o 13 caracteres')
        return isbn


class UploadExcelForm(forms.Form):
    """Formulario para subir archivos Excel con libros."""
    archivo_excel = forms.FileField(
        label='Archivo Excel',
        help_text='Seleccione un archivo .xlsx con los datos de libros',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls'
        })
    )
    actualizar_existentes = forms.BooleanField(
        required=False,
        initial=False,
        label='Actualizar libros existentes',
        help_text='Si está marcado, actualizará libros con el mismo ISBN',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    crear_autores = forms.BooleanField(
        required=False,
        initial=True,
        label='Crear autores automáticamente',
        help_text='Si está marcado, creará autores que no existan en el sistema',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    crear_ejemplares = forms.BooleanField(
        required=False,
        initial=True,
        label='Crear ejemplares',
        help_text='Si está marcado, creará ejemplares según la columna cantidad_ejemplares',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def clean_archivo_excel(self):
        archivo = self.cleaned_data.get('archivo_excel')
        if archivo:
            if not archivo.name.endswith(('.xlsx', '.xls')):
                raise forms.ValidationError('El archivo debe ser un Excel (.xlsx o .xls)')
            
            if archivo.size > 50 * 1024 * 1024:
                raise forms.ValidationError('El archivo no puede ser mayor a 50MB')
        
        return archivo
