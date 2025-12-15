from django import forms
from .models import Socio

class SocioForm(forms.ModelForm):
    class Meta:
        model = Socio
        fields = ['nombre', 'apellido', 'identificacion', 'telefono', 'email', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del socio'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el apellido del socio'
            }),
            'identificacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'DNI, Cédula o ID de Socio'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de teléfono (opcional)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'identificacion': 'Identificación',
            'telefono': 'Teléfono',
            'email': 'Email',
            'activo': 'Activo',
        }
        help_texts = {
            'identificacion': 'DNI, Cédula o ID de Socio (debe ser único)',
            'email': 'El email debe ser único',
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

    def clean_identificacion(self):
        identificacion = self.cleaned_data.get('identificacion')
        if identificacion:
            identificacion = identificacion.strip()
            # Verificar unicidad solo si es un nuevo socio o si cambió la identificación
            if self.instance.pk:
                # Es una edición
                if Socio.objects.filter(identificacion=identificacion).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError('Esta identificación ya está registrada')
            else:
                # Es un nuevo socio
                if Socio.objects.filter(identificacion=identificacion).exists():
                    raise forms.ValidationError('Esta identificación ya está registrada')
        return identificacion

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip().lower()
            # Verificar unicidad solo si es un nuevo socio o si cambió el email
            if self.instance.pk:
                # Es una edición
                if Socio.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError('Este email ya está registrado')
            else:
                # Es un nuevo socio
                if Socio.objects.filter(email=email).exists():
                    raise forms.ValidationError('Este email ya está registrado')
        return email


class UploadExcelForm(forms.Form):
    """Formulario para subir archivos Excel con socios."""
    archivo_excel = forms.FileField(
        label='Archivo Excel',
        help_text='Seleccione un archivo .xlsx con los datos de socios',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls'
        })
    )
    actualizar_existentes = forms.BooleanField(
        required=False,
        initial=False,
        label='Actualizar socios existentes',
        help_text='Si está marcado, actualizará socios con la misma identificación o email',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    crear_usuarios = forms.BooleanField(
        required=False,
        initial=False,
        label='Crear usuarios de sistema',
        help_text='Si está marcado, creará usuarios de Django para los socios (password temporal)',
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