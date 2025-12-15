from django import forms
from .models import Autor

class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = ['nombre', 'apellido', 'nacionalidad', 'fecha_nacimiento', 'biografia']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del autor'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el apellido del autor'
            }),
            'nacionalidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Argentina, México, España...'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'biografia': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ingrese una breve biografía del autor'
            }),
        }
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'nacionalidad': 'Nacionalidad',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'biografia': 'Biografía',
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            nombre = nombre.strip().title()
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')
        if apellido:
            apellido = apellido.strip().title()
        return apellido


class UploadExcelForm(forms.Form):
    """Formulario para subir archivos Excel con autores."""
    archivo_excel = forms.FileField(
        label='Archivo Excel',
        help_text='Seleccione un archivo .xlsx con los datos de autores',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls'
        })
    )
    actualizar_existentes = forms.BooleanField(
        required=False,
        initial=False,
        label='Actualizar autores existentes',
        help_text='Si está marcado, actualizará autores con el mismo nombre y apellido',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def clean_archivo_excel(self):
        archivo = self.cleaned_data.get('archivo_excel')
        if archivo:
            # Validar extensión
            if not archivo.name.endswith(('.xlsx', '.xls')):
                raise forms.ValidationError('El archivo debe ser un Excel (.xlsx o .xls)')
            
            # Validar tamaño (máximo 50MB)
            if archivo.size > 50 * 1024 * 1024:
                raise forms.ValidationError('El archivo no puede ser mayor a 50MB')
        
        return archivo