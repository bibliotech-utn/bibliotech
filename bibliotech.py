#!/usr/bin/env python3
"""
BiblioTech - Script de Automatización
======================================

Script profesional para automatizar el setup, actualización y ejecución
del proyecto Django BiblioTech.

Uso:
    python bibliotech.py              # Setup completo + ejecutar servidor
    python bibliotech.py --setup       # Solo preparar entorno
    python bibliotech.py --update      # Actualizar dependencias y migraciones
    python bibliotech.py --run         # Solo levantar servidor

Autor: Equipo BiblioTech
Versión: 2.0
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import argparse

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

IS_WINDOWS = platform.system() == "Windows"

# Detectar rutas automáticamente
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parent
VENV_NAME = "venv"
VENV_PATH = PROJECT_ROOT / VENV_NAME

# Detectar manage.py automáticamente (buscar recursivamente desde la raíz)
def find_manage_py(start_path):
    """Busca manage.py recursivamente desde un directorio"""
    for root, dirs, files in os.walk(start_path):
        # Ignorar venv y otros directorios comunes
        dirs[:] = [d for d in dirs if d not in ['.git', 'venv', '__pycache__', '.venv', 'node_modules']]
        if 'manage.py' in files:
            return Path(root) / 'manage.py'
    return None

# Detectar requirements.txt (primero en la raíz, luego buscar)
def find_requirements_txt(start_path):
    """Busca requirements.txt desde la raíz hacia abajo"""
    # Primero buscar en la raíz
    root_req = start_path / "requirements.txt"
    if root_req.exists():
        return root_req
    
    # Buscar recursivamente
    for root, dirs, files in os.walk(start_path):
        dirs[:] = [d for d in dirs if d not in ['.git', 'venv', '__pycache__', '.venv', 'node_modules']]
        if 'requirements.txt' in files:
            return Path(root) / 'requirements.txt'
    return None

# Detectar archivos del proyecto
MANAGE_PY_PATH = find_manage_py(PROJECT_ROOT)
REQUIREMENTS_PATH = find_requirements_txt(PROJECT_ROOT)

if MANAGE_PY_PATH:
    DJANGO_PROJECT_DIR = MANAGE_PY_PATH.parent
else:
    DJANGO_PROJECT_DIR = None

# ============================================================================
# UTILIDADES
# ============================================================================

def print_info(msg):
    """Imprime mensaje informativo"""
    print(f"ℹ️  {msg}")

def print_success(msg):
    """Imprime mensaje de éxito"""
    print(f"✅ {msg}")

def print_error(msg):
    """Imprime mensaje de error"""
    print(f"❌ {msg}")

def print_warning(msg):
    """Imprime mensaje de advertencia"""
    print(f"⚠️  {msg}")

def run_command(cmd, check=False, capture_output=False):
    """Ejecuta un comando y retorna el resultado"""
    try:
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=capture_output,
            text=True,
            shell=IS_WINDOWS
        )
        return result
    except subprocess.CalledProcessError as e:
        if not capture_output:
            print_error(f"Error ejecutando: {' '.join(cmd)}")
        return e

def check_python_version():
    """Verifica que la versión de Python sea compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error("Se requiere Python 3.8 o superior")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detectado")
    return True

# ============================================================================
# GESTIÓN DE ENTORNO VIRTUAL
# ============================================================================

def find_venv_python():
    """
    Busca el ejecutable de Python en el venv, probando todas las variantes posibles.
    Retorna el path del Python encontrado, o None si no se encuentra.
    Esta es la función base que todas las demás usan para encontrar el Python del venv.
    """
    if IS_WINDOWS:
        candidates = [
            VENV_PATH / "Scripts" / "python.exe",
            VENV_PATH / "Scripts" / "python",
            VENV_PATH / "Scripts" / "pythonw.exe",
        ]
    else:
        candidates = [
            VENV_PATH / "bin" / "python3",
            VENV_PATH / "bin" / "python",
        ]
    
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return str(candidate)
    
    return None


def venv_exists():
    """
    Verifica si el entorno virtual existe de forma robusta.
    El venv existe SI Y SOLO SI el ejecutable de Python existe.
    Usa find_venv_python() para buscar en todas las ubicaciones posibles.
    """
    return find_venv_python() is not None


def get_venv_python():
    """
    Retorna la ruta completa del Python del entorno virtual.
    Busca el Python en todas las ubicaciones posibles y retorna el encontrado.
    Si no encuentra ninguno, retorna el path estándar esperado.
    """
    # Primero intentar encontrar el Python existente
    found_python = find_venv_python()
    if found_python:
        return found_python
    
    # Si no se encuentra, retornar el path estándar esperado
    if IS_WINDOWS:
        return str(VENV_PATH / "Scripts" / "python.exe")
    else:
        return str(VENV_PATH / "bin" / "python3")


def create_venv():
    """Crea el entorno virtual si no existe"""
    if venv_exists():
        print_info("Entorno virtual ya existe")
        return True
    
    print_info("Creando entorno virtual...")
    try:
        # Usar venv (estándar de Python 3.3+)
        run_command([sys.executable, "-m", "venv", str(VENV_PATH)], check=True)
        
        # Buscar el Python del venv en todas las ubicaciones posibles
        python_path = find_venv_python()
        
        if python_path:
            print_success("Entorno virtual creado correctamente")
            print_info(f"Python del venv: {python_path}")
            return True
        else:
            print_error("Entorno virtual creado, pero Python no encontrado")
            print_info(f"Buscado en: {VENV_PATH}")
            if IS_WINDOWS:
                print_info("Ubicaciones esperadas: venv/Scripts/python.exe")
            else:
                print_info("Ubicaciones esperadas: venv/bin/python3 o venv/bin/python")
            return False
        
    except Exception as e:
        print_error(f"Error creando entorno virtual: {e}")
        return False


# ============================================================================
# INSTALACIÓN Y ACTUALIZACIÓN
# ============================================================================

def ensure_pip():
    """Asegura que pip esté disponible en el entorno virtual"""
    if not venv_exists():
        print_error("Entorno virtual no existe")
        return False
    
    # Buscar el Python del venv (puede estar en diferentes ubicaciones)
    python_cmd = find_venv_python()
    
    if not python_cmd:
        print_error("Python del venv no encontrado")
        print_info(f"Buscado en: {VENV_PATH}")
        return False
    
    print_info("Verificando pip en el entorno virtual...")
    
    # Verificar si pip está disponible
    result = run_command(
        [python_cmd, "-m", "pip", "--version"],
        check=False,
        capture_output=True
    )
    
    if result.returncode == 0:
        print_success("pip está disponible")
        return True
    
    # Si pip no está disponible, inicializarlo
    print_info("pip no encontrado, inicializando con ensurepip...")
    result = run_command(
        [python_cmd, "-m", "ensurepip", "--upgrade"],
        check=False
    )
    
    if result.returncode == 0:
        print_success("pip inicializado correctamente")
        return True
    else:
        print_error("Error inicializando pip")
        return False


def install_dependencies():
    """Instala o actualiza las dependencias desde requirements.txt usando python -m pip"""
    if not REQUIREMENTS_PATH or not REQUIREMENTS_PATH.exists():
        print_error(f"Archivo requirements.txt no encontrado")
        print_info(f"Buscado en: {PROJECT_ROOT}")
        return False
    
    if not venv_exists():
        print_error("Entorno virtual no existe")
        return False
    
    # Buscar el Python del venv (puede estar en diferentes ubicaciones)
    python_cmd = find_venv_python()
    
    if not python_cmd:
        print_error("Python del venv no encontrado")
        print_info(f"Buscado en: {VENV_PATH}")
        return False
    
    print_info("Instalando/actualizando dependencias...")
    print_info(f"Usando: {REQUIREMENTS_PATH}")
    
    # Actualizar pip primero
    print_info("Actualizando pip...")
    result = run_command(
        [python_cmd, "-m", "pip", "install", "--upgrade", "pip"],
        check=False
    )
    
    if result.returncode != 0:
        print_warning("Error actualizando pip, continuando de todas formas...")
    
    # Instalar dependencias
    print_info("Instalando dependencias desde requirements.txt...")
    result = run_command(
        [python_cmd, "-m", "pip", "install", "-r", str(REQUIREMENTS_PATH)],
        check=False
    )
    
    if result.returncode == 0:
        print_success("Dependencias instaladas correctamente")
        return True
    else:
        print_error("Error instalando dependencias")
        return False


def run_migrations():
    """Ejecuta las migraciones de Django"""
    if not MANAGE_PY_PATH or not MANAGE_PY_PATH.exists():
        print_error(f"manage.py no encontrado")
        print_info(f"Buscado desde: {PROJECT_ROOT}")
        return False
    
    if not venv_exists():
        print_error("Entorno virtual no existe")
        return False
    
    # Buscar el Python del venv (puede estar en diferentes ubicaciones)
    python_cmd = find_venv_python()
    
    if not python_cmd:
        print_error("Python del venv no encontrado")
        return False
    
    print_info("Ejecutando migraciones...")
    
    # Cambiar al directorio del proyecto Django
    os.chdir(DJANGO_PROJECT_DIR)
    
    result = run_command(
        [python_cmd, "manage.py", "migrate"],
        check=False
    )
    
    if result.returncode == 0:
        print_success("Migraciones ejecutadas correctamente")
        return True
    else:
        print_warning("Algunas migraciones pueden haber fallado")
        return False


def collect_static():
    """Recolecta archivos estáticos"""
    if not MANAGE_PY_PATH or not MANAGE_PY_PATH.exists():
        return False
    
    if not venv_exists():
        return False
    
    # Buscar el Python del venv (puede estar en diferentes ubicaciones)
    python_cmd = find_venv_python()
    
    if not python_cmd:
        return False
    
    print_info("Recolectando archivos estáticos...")
    
    # Cambiar al directorio del proyecto Django
    os.chdir(DJANGO_PROJECT_DIR)
    
    result = run_command(
        [python_cmd, "manage.py", "collectstatic", "--noinput"],
        check=False
    )
    
    if result.returncode == 0:
        print_success("Archivos estáticos recolectados")
        return True
    else:
        print_warning("Error recolectando archivos estáticos (puede ser normal si no hay archivos estáticos)")
        return False


# ============================================================================
# VERIFICACIÓN
# ============================================================================

def verify_setup():
    """Verifica que el setup esté completo"""
    print_info("Verificando setup...")
    all_ok = True
    
    checks = [
        (VENV_PATH, "Entorno virtual"),
        (MANAGE_PY_PATH, "manage.py"),
        (REQUIREMENTS_PATH, "requirements.txt"),
    ]
    
    for path, name in checks:
        if path and path.exists():
            print_success(f"{name} encontrado")
        else:
            print_error(f"{name} no encontrado en: {path}")
            all_ok = False
    
    return all_ok


# ============================================================================
# EJECUCIÓN DEL SERVIDOR
# ============================================================================

def run_server():
    """Levanta el servidor de desarrollo de Django"""
    if not MANAGE_PY_PATH or not MANAGE_PY_PATH.exists():
        print_error(f"manage.py no encontrado")
        print_info(f"Buscado desde: {PROJECT_ROOT}")
        return False
    
    if not venv_exists():
        print_error("Entorno virtual no existe. Ejecuta primero: python bibliotech.py --setup")
        return False
    
    # Buscar el Python del venv (puede estar en diferentes ubicaciones)
    python_cmd = find_venv_python()
    
    if not python_cmd:
        print_error("Python del venv no encontrado")
        print_info("Ejecuta primero: python bibliotech.py --setup")
        return False
    
    print_info("Iniciando servidor de desarrollo...")
    print_info("Presiona Ctrl+C para detener el servidor")
    print_info("Servidor disponible en: http://127.0.0.1:8000")
    
    # Cambiar al directorio del proyecto Django
    os.chdir(DJANGO_PROJECT_DIR)
    
    try:
        # Ejecutar servidor (bloqueante)
        run_command(
            [python_cmd, "manage.py", "runserver"],
            check=True
        )
    except KeyboardInterrupt:
        print_info("\nServidor detenido por el usuario")
        return True
    except Exception as e:
        print_error(f"Error ejecutando servidor: {e}")
        return False


# ============================================================================
# FUNCIONES PRINCIPALES
# ============================================================================

def setup():
    """Prepara el entorno completo"""
    print_info("=" * 60)
    print_info("BiblioTech - Setup del Proyecto")
    print_info("=" * 60)
    
    if not check_python_version():
        return False
    
    if not create_venv():
        return False
    
    if not ensure_pip():
        return False
    
    if not install_dependencies():
        return False
    
    if not run_migrations():
        return False
    
    collect_static()  # No crítico si falla
    
    print_success("Setup completado correctamente")
    return True


def update():
    """Actualiza dependencias y migraciones"""
    print_info("=" * 60)
    print_info("BiblioTech - Actualización")
    print_info("=" * 60)
    
    if not venv_exists():
        print_error("Entorno virtual no existe. Ejecuta primero: python bibliotech.py --setup")
        return False
    
    if not ensure_pip():
        return False
    
    if not install_dependencies():
        return False
    
    if not run_migrations():
        return False
    
    collect_static()  # No crítico si falla
    
    print_success("Actualización completada")
    return True


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Script de automatización para BiblioTech",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python bibliotech.py              # Setup completo + ejecutar servidor
  python bibliotech.py --setup       # Solo preparar entorno
  python bibliotech.py --update      # Actualizar dependencias y migraciones
  python bibliotech.py --run         # Solo levantar servidor
        """
    )
    
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Solo preparar el entorno (no ejecutar servidor)"
    )
    
    parser.add_argument(
        "--update",
        action="store_true",
        help="Actualizar dependencias y migraciones (no ejecutar servidor)"
    )
    
    parser.add_argument(
        "--run",
        action="store_true",
        help="Solo levantar el servidor (asume que el entorno ya está configurado)"
    )
    
    args = parser.parse_args()
    
    # Volver al directorio raíz del proyecto
    os.chdir(PROJECT_ROOT)
    
    if args.setup:
        success = setup()
        sys.exit(0 if success else 1)
    elif args.update:
        success = update()
        sys.exit(0 if success else 1)
    elif args.run:
        success = run_server()
        sys.exit(0 if success else 1)
    else:
        # Modo por defecto: setup completo + ejecutar servidor
        if setup():
            print_info("=" * 60)
            run_server()
        else:
            print_error("Setup falló, no se puede ejecutar el servidor")
            sys.exit(1)


if __name__ == "__main__":
    main()
