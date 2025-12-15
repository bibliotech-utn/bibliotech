from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Socio

class RegistroSocioForm(UserCreationForm):
    nombre = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nombre'
    }))
    apellido = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Apellido'
    }))
    identificacion = forms.CharField(max_length=15, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'DNI o Identificación'
    }))
    telefono = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Teléfono (opcional)'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'correo@ejemplo.com'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'nombre', 'apellido', 'identificacion', 'telefono']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Socio.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado')
        return email

    def clean_identificacion(self):
        identificacion = self.cleaned_data.get('identificacion')
        if Socio.objects.filter(identificacion=identificacion).exists():
            raise forms.ValidationError('Esta identificación ya está registrada')
        return identificacion

    def save(self, commit=True):
        from django.db import transaction
        
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            with transaction.atomic():
                user.save()
                socio = Socio.objects.create(
                    user=user,
                    nombre=self.cleaned_data['nombre'],
                    apellido=self.cleaned_data['apellido'],
                    identificacion=self.cleaned_data['identificacion'],
                    telefono=self.cleaned_data.get('telefono', ''),
                    email=self.cleaned_data['email']
                )
        return user

class LoginSocioForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nombre de usuario'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Contraseña'
    }))

