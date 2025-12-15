"""
URL configuration for biblioteca project.
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('landing/', views.landing, name='landing'),
    path('presentacion/', views.presentacion, name='presentacion'),
    path('login/socio/', views.login_socio, name='login_socio'),
    path('registro/socio/', views.registro_socio, name='registro_socio'),
    path('login/personal/', views.login_personal, name='login_personal'),
    path('logout/', views.logout_view, name='logout'),
    path('ayuda/personal/', views.ayuda_personal, name='ayuda_personal'),
    path('ayuda/socio/', views.ayuda_socio, name='ayuda_socio'),
    path("libros/", include("gestion_libros.urls")),
    path("prestamos/", include("gestion_prestamos.urls")),
    path("autores/", include("gestion_autores.urls")),
    path("socios/", include("gestion_socios.urls")),
    path("socio/", include("gestion_libros.urls_socios")),
    path("personal/", include("gestion_personal.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)