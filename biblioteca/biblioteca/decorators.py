from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from gestion_personal.models import Personal
from gestion_socios.models import Socio


def es_personal_required(view_func):
    """
    Decorador para verificar que el usuario es personal de la biblioteca.
    
    Si el usuario no tiene un registro Personal asociado, se crea automáticamente
    si el usuario es staff. De lo contrario, se verifica si es socio.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión como personal para acceder a esta sección.')
            login_url = reverse('login_personal')
            next_url = request.get_full_path()
            return redirect(f'{login_url}?next={next_url}')
        
        # Usar filter().first() en lugar de get() para evitar DoesNotExist
        personal = Personal.objects.filter(user=request.user).first()
        
        if personal:
            if not personal.activo:
                messages.error(request, 'Tu cuenta de personal está inactiva.')
                return redirect('home')
            return view_func(request, *args, **kwargs)
        
        # Si no existe Personal pero es staff, crear automáticamente
        if request.user.is_staff:
            personal = Personal.objects.create(
                user=request.user,
                nombre=request.user.first_name or "Admin",
                apellido=request.user.last_name or "User",
                cargo="Administrador",
                activo=True
            )
            return view_func(request, *args, **kwargs)
        
        # Verificar si es socio
        socio = Socio.objects.filter(user=request.user).first()
        if socio:
            messages.error(request, 'No tenés permisos para acceder a esta sección.')
            return redirect('home')
        
        # Si no es ni Personal ni Socio
        messages.error(request, 'No tenés permisos para acceder a esta sección.')
        login_url = reverse('login_personal')
        next_url = request.get_full_path()
        return redirect(f'{login_url}?next={next_url}')
    
    return _wrapped_view


def es_socio_required(view_func):
    """
    Decorador para verificar que el usuario es un socio.
    
    Si el usuario no tiene un registro Socio asociado, se verifica si es Personal.
    No se crea automáticamente un Socio para evitar problemas de integridad.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión como socio para acceder a esta sección.')
            login_url = reverse('login_socio')
            next_url = request.get_full_path()
            return redirect(f'{login_url}?next={next_url}')
        
        # Usar filter().first() en lugar de get() para evitar DoesNotExist
        socio = Socio.objects.filter(user=request.user).first()
        
        if socio:
            if not socio.activo:
                messages.error(request, 'Tu cuenta está inactiva. Contacta al administrador.')
                return redirect('home')
            return view_func(request, *args, **kwargs)
        
        # Verificar si es Personal
        personal = Personal.objects.filter(user=request.user).first()
        if personal:
            messages.error(request, 'No tenés permisos para acceder a esta sección.')
            return redirect('home')
        
        # Si no es ni Socio ni Personal
        messages.error(request, 'No tenés permisos para acceder a esta sección.')
        login_url = reverse('login_socio')
        next_url = request.get_full_path()
        return redirect(f'{login_url}?next={next_url}')
    
    return _wrapped_view
