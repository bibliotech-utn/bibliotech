from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from gestion_socios.forms_auth import LoginSocioForm, RegistroSocioForm
from gestion_socios.models import Socio
from gestion_personal.forms import LoginPersonalForm
from gestion_personal.models import Personal

def home(request):
    """Página principal con opciones de login"""
    return render(request, "home.html")

def login_socio(request):
    """Login para socios"""
    if request.user.is_authenticated:
        # Si ya está autenticado, redirigir según el parámetro next o a home
        next_url = request.GET.get('next', 'home')
        return redirect(next_url)
    
    if request.method == 'POST':
        form = LoginSocioForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Verificar que el usuario sea un socio
                socio = Socio.objects.filter(user=user).first()
                if socio:
                    if socio.activo:
                        login(request, user)
                        messages.success(request, 'Sesión iniciada correctamente.')
                        next_url = request.GET.get('next', 'home')
                        return redirect(next_url)
                    else:
                        messages.error(request, 'Tu cuenta está inactiva. Contacta al administrador.')
                else:
                    messages.error(request, 'No tenés permisos para acceder a esta sección.')
            else:
                messages.error(request, 'Credenciales incorrectas.')
    else:
        form = LoginSocioForm()
    
    return render(request, 'auth/login_socio.html', {'form': form})

def registro_socio(request):
    """Registro para nuevos socios"""
    from django.db import transaction
    import logging
    
    logger = logging.getLogger('gestion_socios')
    
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegistroSocioForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                messages.success(request, 'Registro exitoso. Ahora podés iniciar sesión.')
                return redirect('login_socio')
            except Exception as e:
                logger.error(f'Error al registrar socio: {str(e)}', exc_info=True)
                messages.error(request, 'Ocurrió un error al registrar tu cuenta. Por favor, intentá nuevamente.')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = RegistroSocioForm()
    
    return render(request, 'auth/registro_socio.html', {'form': form})

def login_personal(request):
    """Login para personal de la biblioteca"""
    if request.user.is_authenticated:
        # Si ya está autenticado, redirigir según el parámetro next o a home
        next_url = request.GET.get('next', 'home')
        return redirect(next_url)
    
    if request.method == 'POST':
        form = LoginPersonalForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Verificar que el usuario sea personal
                personal = Personal.objects.filter(user=user).first()
                if personal:
                    if personal.activo:
                        login(request, user)
                        messages.success(request, 'Sesión iniciada correctamente.')
                        next_url = request.GET.get('next', 'home')
                        return redirect(next_url)
                    else:
                        messages.error(request, 'Tu cuenta está inactiva. Contacta al administrador.')
                elif user.is_staff:
                    # Si es staff, también puede acceder
                    login(request, user)
                    messages.success(request, 'Sesión iniciada correctamente.')
                    next_url = request.GET.get('next', 'home')
                    return redirect(next_url)
                else:
                    messages.error(request, 'No tenés permisos para acceder a esta sección.')
            else:
                messages.error(request, 'Credenciales incorrectas.')
    else:
        form = LoginPersonalForm()
    
    return render(request, 'auth/login_personal.html', {'form': form})

def logout_view(request):
    """Cerrar sesión"""
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('home')

def ayuda_personal(request):
    """Página de ayuda para personal de biblioteca"""
    return render(request, "ayuda_personal.html")

def ayuda_socio(request):
    """Página de ayuda para socios"""
    return render(request, "ayuda_socio.html")

def landing(request):
    """Landing page comercial del sistema"""
    return render(request, "landing.html")

def presentacion(request):
    """Presentación pitch deck de BiblioTech"""
    return render(request, "presentacion_bibliotech.html")
