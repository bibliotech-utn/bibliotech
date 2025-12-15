BiblioTech – Sistema de Gestión de Biblioteca

BiblioTech es un sistema de gestión de biblioteca desarrollado como proyecto académico utilizando Django y Python.
Permite administrar libros, ejemplares, socios, personal y préstamos, con una interfaz web pensada para uso en instituciones educativas.

Repositorio público oficial:
https://github.com/bibliotech-utn/bibliotech

El repositorio forma parte de la organización del grupo de trabajo.

Objetivo del sistema

Administrar el catálogo de libros y ejemplares de una biblioteca.

Registrar y controlar préstamos y devoluciones, incluyendo estados y vencimientos.

Gestionar socios y personal, diferenciando permisos y vistas según el rol.

Facilitar tareas operativas como búsquedas, filtros, exportación a CSV e importación desde Excel.

Landing y presentación del proyecto

El sistema incluye dos vistas institucionales, pensadas para contextualizar el proyecto y facilitar su presentación académica y técnica.

Landing page institucional

URL: http://127.0.0.1:8000/landing/

Página de introducción general al sistema. Presenta BiblioTech de forma resumida y orientada a la primera impresión, explicando el propósito del proyecto y su contexto de uso.

Presentación del sistema

URL: http://127.0.0.1:8000/presentacion/

Vista explicativa que describe el funcionamiento del sistema, sus módulos principales y el enfoque adoptado en el desarrollo del proyecto.

Ambas vistas están implementadas como templates HTML y se encuentran disponibles una vez que el servidor de desarrollo está en ejecución.

Funcionalidades principales
Libros y ejemplares

Alta, baja lógica, modificación y consulta de libros.

Gestión de ejemplares físicos asociados a cada libro.

Estados de ejemplar: disponible, prestado, reparación y perdido.

Autores

Registro y edición de autores.

Asociación de libros a autores.

Socios

Registro de socios con datos de identificación y contacto.

Asociación opcional a usuarios del sistema para acceso al panel de socio.

Personal

Registro de personal de biblioteca vinculado a usuarios del sistema.

Acceso a vistas administrativas y de gestión.

Préstamos y reservas

Registro de préstamos de ejemplares a socios.

Control de fechas de devolución esperada y real.

Estados del préstamo: pendiente, devuelto y vencido.

Registro y gestión de reservas cuando no hay ejemplares disponibles.

Importación y exportación de datos

Importación desde archivos Excel (libros, socios y autores) con historial de importaciones.

Exportación de listados a CSV (libros, socios y préstamos).

Interfaz y navegación

Templates con estructura común mediante base.html y bloques reutilizables.

Navegación diferenciada para personal y socios.

Paginación y búsqueda en los principales listados.

Tecnologías utilizadas
Backend

Python

Django

SQLite (entorno de desarrollo)

Frontend

HTML y CSS

Tailwind CSS (mediante CDN y estilos personalizados)

DaisyUI (componentes sobre Tailwind)

Otros

Pandas y OpenPyXL para importación de datos desde Excel.

Módulo estándar de logging de Python para registro en archivos.

Requisitos previos

Python 3.x instalado.

Acceso a Internet para cargar los recursos de Tailwind y fuentes desde CDN.

Entorno virtual de Python (recomendado).

Instalación
1. Clonar el repositorio
git clone https://github.com/bibliotech-utn/bibliotech.git
cd bibliotech

2. Crear y activar entorno virtual (recomendado)
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
# source venv/bin/activate


El entorno virtual no forma parte del repositorio; se crea localmente en cada máquina de desarrollo.

3. Instalar dependencias
pip install -r requirements.txt

4. Aplicar migraciones
cd biblioteca
python manage.py migrate

5. Crear usuario administrador (opcional pero recomendado)
python manage.py createsuperuser

Ejecución local

Desde la carpeta biblioteca:

python manage.py runserver

Accesos principales

Sitio principal: http://127.0.0.1:8000/

Landing: /landing/

Presentación: /presentacion/

Rutas de uso frecuente

Login personal: /login/personal/

Login socios: /login/socio/

Registro de socios: /registro/socio/

Libros (personal): /libros/

Socios (personal): /socios/

Préstamos (personal): /prestamos/

Uso del script bibliotech.py (opcional)

El proyecto incluye un script auxiliar bibliotech.py ubicado en la raíz del repositorio.
Funciona como un punto de entrada simplificado para preparar y ejecutar el sistema.

Automatiza:

Creación del entorno virtual (si no existe).

Instalación de dependencias.

Aplicación de migraciones.

Ejecución del servidor de desarrollo.

No reemplaza el uso estándar de manage.py, sino que lo complementa como atajo operativo.

Estructura general del proyecto
.
├── bibliotech.py              # Script auxiliar
├── requirements.txt           # Dependencias
├── README.md                  # Documentación principal
└── biblioteca/
    ├── manage.py
    ├── biblioteca/            # Configuración del proyecto
    ├── gestion_autores/
    ├── gestion_libros/
    ├── gestion_socios/
    ├── gestion_personal/
    ├── gestion_prestamos/
    ├── gestion_importaciones/
    ├── templates/
    ├── static/
    └── presentacion/


Dentro de biblioteca/templates/ se encuentran:

landing.html

presentacion_bibliotech.html

En biblioteca/presentacion/ se agrupan los recursos de apoyo para la exposición.

Video de presentación

El proyecto cuenta con un video de presentación que resume:

La idea general del sistema.

El enfoque como MVP.

Una visión de escalabilidad futura.

Ubicación:

biblioteca/presentacion/video/


El video acompaña la landing y la presentación institucional, y puede utilizarse como soporte en la defensa oral o revisiones de portfolio académico.

Modelado y organización (resumen técnico)

Modelos con tipos de campo adecuados y relaciones mediante ForeignKey y OneToOneField.

Implementación de __str__ para legibilidad en el administrador.

Vistas basadas en funciones con separación clara de responsabilidades.

Control de acceso mediante decoradores según tipo de usuario.

URLs organizadas por aplicación utilizando include y namespaces.

Templates con herencia y componentes reutilizables.

Autores

Proyecto desarrollado como trabajo académico para la UTN FRLP por:

Quevedo Ramiro

Zunino Juan

Stella Cáceres

Los créditos también se encuentran en el pie de página de la aplicación.

Notas técnicas y consideraciones

Proyecto orientado a entorno de desarrollo con SQLite.

Logs generados en la carpeta logs/ (ignorados por Git).

No se versionan entornos virtuales.

Las dependencias deben instalarse en un entorno limpio para evitar conflictos.
