from django import forms
from .models import Prestamo
from gestion_socios.models import Socio
from gestion_libros.models import Ejemplar
from django.utils import timezone
from datetime import timedelta

class PrestamoForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = ['socio', 'ejemplar', 'fecha_devolucion_esperada', 'observaciones']
        widgets = {
            'socio': forms.Select(attrs={
                'class': 'form-control'
            }),
            'ejemplar': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fecha_devolucion_esperada': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales (opcional)'
            }),
        }
        labels = {
            'socio': 'Socio',
            'ejemplar': 'Ejemplar',
            'fecha_devolucion_esperada': 'Fecha de Devolución Esperada',
            'observaciones': 'Observaciones',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo socios activos
        self.fields['socio'].queryset = Socio.objects.filter(activo=True).order_by('apellido', 'nombre')
        # Filtrar solo ejemplares disponibles
        self.fields['ejemplar'].queryset = Ejemplar.objects.filter(estado='DISPONIBLE').select_related('libro').order_by('libro__titulo', 'codigo')
        
        # Establecer fecha mínima (hoy)
        hoy = timezone.now().date()
        self.fields['fecha_devolucion_esperada'].widget.attrs['min'] = hoy.strftime('%Y-%m-%d')
        
        # Mensajes de ayuda
        if not Socio.objects.filter(activo=True).exists():
            self.fields['socio'].widget.attrs['disabled'] = True
            self.fields['socio'].help_text = 'No hay socios activos disponibles'
        
        if not Ejemplar.objects.filter(estado='DISPONIBLE').exists():
            self.fields['ejemplar'].widget.attrs['disabled'] = True
            self.fields['ejemplar'].help_text = 'No hay ejemplares disponibles'

    def clean_ejemplar(self):
        ejemplar = self.cleaned_data.get('ejemplar')
        if ejemplar:
            if ejemplar.estado != 'DISPONIBLE':
                raise forms.ValidationError('Este ejemplar no está disponible para préstamo')
            # Verificar si el ejemplar ya tiene un préstamo pendiente
            prestamo_pendiente = Prestamo.objects.filter(
                ejemplar=ejemplar,
                estado='PENDIENTE'
            ).exists()
            if prestamo_pendiente:
                raise forms.ValidationError('Este ejemplar ya tiene un préstamo pendiente')
        return ejemplar

    def clean_socio(self):
        socio = self.cleaned_data.get('socio')
        if socio:
            if not socio.activo:
                raise forms.ValidationError('Este socio no está activo')
            
            from gestion_prestamos.services import PrestamoService
            puede_prestar, mensaje_error = PrestamoService.validar_limite_prestamos(socio)
            if not puede_prestar:
                raise forms.ValidationError(mensaje_error)
        
        return socio

    def clean_fecha_devolucion_esperada(self):
        fecha_devolucion = self.cleaned_data.get('fecha_devolucion_esperada')
        hoy = timezone.now().date()
        
        if fecha_devolucion:
            if fecha_devolucion < hoy:
                raise forms.ValidationError('La fecha de devolución no puede ser anterior a hoy')
            
            # Validar que no sea más de 90 días en el futuro
            fecha_maxima = hoy + timedelta(days=90)
            if fecha_devolucion > fecha_maxima:
                raise forms.ValidationError('La fecha de devolución no puede ser más de 90 días en el futuro')
        
        return fecha_devolucion

    def save(self, commit=True):
        from django.db import transaction
        
        prestamo = super().save(commit=False)
        if commit:
            with transaction.atomic():
                # Verificar nuevamente que el ejemplar esté disponible (evitar race condition)
                ejemplar_actualizado = Ejemplar.objects.select_for_update().filter(
                    id=prestamo.ejemplar.id,
                    estado='DISPONIBLE'
                ).first()
                
                if not ejemplar_actualizado:
                    raise ValueError('El ejemplar ya no está disponible')
                
                # Verificar que no haya préstamo pendiente
                prestamo_pendiente = Prestamo.objects.filter(
                    ejemplar=ejemplar_actualizado,
                    estado='PENDIENTE'
                ).exists()
                
                if prestamo_pendiente:
                    raise ValueError('El ejemplar ya tiene un préstamo pendiente')
                
                # Marcar el ejemplar como prestado
                ejemplar_actualizado.estado = 'PRESTADO'
                ejemplar_actualizado.save(update_fields=['estado'])
                prestamo.ejemplar = ejemplar_actualizado
                prestamo.save()
        return prestamo
