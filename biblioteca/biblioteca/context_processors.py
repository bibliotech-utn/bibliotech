from django.conf import settings
from django.core.cache import cache
from gestion_personal.models import Personal
from gestion_socios.models import Socio


def user_type(request):
    """
    Context processor para determinar el tipo de usuario.
    
    Usa filter().first() en lugar de get() para evitar excepciones DoesNotExist.
    """
    context = {
        'es_personal': False,
        'es_socio': False,
    }
    
    if not request.user.is_authenticated:
        return context
    
    cache_key = f'user_type_{request.user.id}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    
    # Usar filter().first() para evitar DoesNotExist
    personal = Personal.objects.filter(user=request.user).first()
    if personal and personal.activo:
        context['es_personal'] = True
    elif request.user.is_staff:
        context['es_personal'] = True
    else:
        socio = Socio.objects.filter(user=request.user).first()
        if socio and socio.activo:
            context['es_socio'] = True
    
    cache.set(cache_key, context, 300)
    return context

def site_name(request):
    """Context processor para el nombre del sitio"""
    return {
        'SITE_NAME': settings.SITE_NAME
    }


