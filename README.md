## BiblioTech – Sistema de Gestión de Biblioteca

BiblioTech es un sistema de gestión de biblioteca desarrollado como proyecto académico utilizando Django y Python.  
Permite administrar libros, ejemplares, socios, personal y préstamos, con una interfaz web pensada para uso en instituciones educativas.

**Repositorio público oficial**: [https://github.com/bibliotech-utn/bibliotech](https://github.com/bibliotech-utn/bibliotech)  
El repositorio forma parte de la organización del grupo de trabajo.

---

## Objetivo del sistema

- **Administrar el catálogo** de libros y ejemplares de una biblioteca.
- **Registrar y controlar préstamos** y devoluciones, incluyendo estados y vencimientos.
- **Gestionar socios y personal**, diferenciando sus permisos y vistas.
- **Facilitar tareas operativas** (búsquedas, filtros, exportación a CSV e importación desde Excel).

---

## Funcionalidades principales

- **Libros y ejemplares**
  - Alta, baja lógica, modificación y consulta de libros.
  - Gestión de ejemplares físicos asociados a cada libro.
  - Estados de ejemplar (disponible, prestado, reparación, perdido).

- **Autores**
  - Registro y edición de autores.
  - Asociación de libros a autores.

- **Socios**
  - Registro de socios con datos de identificación y contacto.
  - Asociación opcional a usuarios del sistema para acceso a panel de socio.

- **Personal**
  - Registro de personal de biblioteca vinculado a usuarios del sistema.
  - Acceso a vistas administrativas y de gestión.

- **Préstamos y reservas**
  - Registro de préstamos de ejemplares a socios.
  - Control de fechas de devolución esperada y real.
  - Estados del préstamo (pendiente, devuelto, vencido).
  - Registro y gestión de reservas de libros cuando no hay ejemplares disponibles.

- **Importación y exportación de datos**
  - Importación desde archivos Excel (libros, socios, autores) con historial de importaciones.
  - Exportación de listados a CSV (libros, socios, préstamos).

- **Interfaz y navegación**
  - Templates con estructura común mediante `base.html` y bloques reutilizables.
  - Navegación diferenciada para personal y socios.
  - Paginación y búsqueda en los principales listados.

---

## Tecnologías utilizadas

- **Backend**
  - Python
  - Django
  - SQLite (entorno de desarrollo)

- **Frontend**
  - HTML y CSS
  - Tailwind CSS (mediante CDN y estilos personalizados)
  - DaisyUI (componentes sobre Tailwind)

- **Otros**
  - Pandas y OpenPyXL para importación de datos desde Excel.
  - Módulo estándar de logging de Python para registro en archivos.

---

## Requisitos previos

- Python 3.x instalado.
- Acceso a Internet para cargar los recursos de Tailwind y fuentes desde CDN.
- Opcional: entorno virtual de Python (recomendado para aislar dependencias).

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/bibliotech-utn/bibliotech.git
cd bibliotech
```

### 2. Crear y activar entorno virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
# source venv/bin/activate
```

> El entorno virtual no forma parte del repositorio; se crea localmente en cada máquina de desarrollo.

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones

```bash
cd biblioteca
python manage.py migrate
```

### 5. Crear usuario administrador (opcional pero recomendado)

```bash
python manage.py createsuperuser
```

---

## Ejecución local

Desde la carpeta `biblioteca`:

```bash
python manage.py runserver
```

Accesos principales:

- **Sitio principal**: `http://127.0.0.1:8000/`

### Rutas de uso frecuente

- **Login personal**: `/login/personal/`
- **Login socios**: `/login/socio/`
- **Registro de socios**: `/registro/socio/`
- **Módulo libros (personal)**: `/libros/`
- **Módulo socios (personal)**: `/socios/`
- **Módulo préstamos (personal)**: `/prestamos/`

---

## Uso del script `bibliotech.py` (opcional)

El proyecto incluye un script auxiliar `bibliotech.py` en la raíz, pensado para automatizar tareas habituales en desarrollo:

- Creación de entorno virtual.
- Instalación de dependencias.
- Ejecución de migraciones.
- Ejecución del servidor de desarrollo.

Este script actúa como un punto de entrada unificado para preparar y ejecutar el sistema. Internamente realiza los mismos pasos que se ejecutarían manualmente con `manage.py` y los comandos de Python: prepara el entorno virtual, instala las dependencias de `requirements.txt`, aplica las migraciones y, si corresponde, inicia el servidor de desarrollo.

No reemplaza el uso estándar de `manage.py`, sino que funciona como un wrapper/atajo opcional para simplificar el arranque del proyecto desde un único archivo.

---

## Estructura general del proyecto

Estructura simplificada de los elementos principales:

```text
.
├── bibliotech.py                          # Script auxiliar/atajo para ejecutar el proyecto
├── requirements.txt                       # Dependencias de Python
├── README.md                              # Documentación principal del proyecto
└── biblioteca/
    ├── manage.py                          # Punto de entrada clásico de Django
    ├── biblioteca/                        # Configuración del proyecto
    │   ├── settings.py
    │   ├── urls.py
    │   ├── views.py
    │   └── ...
    ├── gestion_autores/       # App: autores
    ├── gestion_libros/        # App: libros y ejemplares
    ├── gestion_socios/        # App: socios
    ├── gestion_personal/      # App: personal de biblioteca
    ├── gestion_prestamos/     # App: préstamos y reservas
    ├── gestion_importaciones/             # App: historial de importaciones
    ├── templates/                         # Templates HTML (base y módulos)
    ├── static/                            # Recursos estáticos (CSS adicionales)
    └── presentacion/                      # Recursos asociados a la presentación institucional

Dentro de `biblioteca/templates/` se encuentran las vistas de presentación en HTML:

- `landing.html`
- `presentacion_bibliotech.html`

En `biblioteca/presentacion/` se agrupan los recursos de apoyo para la exposición, incluyendo el video demo en la subcarpeta `video/`.

---

## Video de presentación

El proyecto cuenta con un video de presentación que resume la idea general del sistema, su posible escalabilidad y el enfoque adoptado como solución de gestión bibliotecaria.

Este material se almacena dentro de la estructura del proyecto, bajo:

- `biblioteca/presentacion/video/`

El archivo de video (por ejemplo, `Publicidad de BiblioTech.mp4`) acompaña la landing y la presentación institucional (`landing.html` y `presentacion_bibliotech.html` en `biblioteca/templates/`), y puede utilizarse como soporte en la defensa oral o en revisiones de portfolio.
```

La app `theme` se utiliza para centralizar estilos basados en Tailwind CSS. El archivo generado de Tailwind no se mantiene en el repositorio; se puede volver a generar con las herramientas indicadas en `theme/package.json` si se requiere ajustar el diseño.

---

## Modelado y organización (resumen técnico)

- **Modelos**
  - Uso de tipos de campo acordes (por ejemplo, `DateField`, `DateTimeField`, `BooleanField`, `EmailField`).
  - Relaciones definidas con `ForeignKey` y `OneToOneField` según corresponda (socios, personal, libros, ejemplares, préstamos, reservas).
  - Implementación de `__str__` para facilitar la lectura en el administrador de Django y en consultas.
  - Uso de `Meta` para ordenar listados y configurar nombres legibles.

- **Vistas y URLs**
  - Vistas basadas en funciones, separando lógica de negocio, acceso a datos y presentación.
  - Decoradores para controlar el acceso según tipo de usuario (personal o socio).
  - Listados con paginación y criterios de búsqueda reutilizables mediante utilidades comunes.
  - URLs organizadas por app mediante `include`, con namespaces (`app_name`) para evitar colisiones de nombres.

- **Templates**
  - Template base `base.html` con bloques (`block`) para contenido específico de cada vista.
  - Componentes reutilizables (por ejemplo, tablas, paginación y campos de formulario).
  - Templates específicos por módulo (`gestion_libros`, `gestion_socios`, etc.) que extienden de la base.

---

## Autores

Este proyecto fue desarrollado como trabajo académico para la UTN FRLP por:

- **Quevedo Ramiro**
- **Zunino Juan**
- **Stella Cáceres**

Los créditos también se encuentran en el pie de página de la aplicación (templates).

---

## Notas técnicas y consideraciones

- El proyecto está pensado para ejecutarse en entorno de desarrollo con SQLite.  
  Para despliegues en producción se pueden utilizar otras bases de datos configurando las variables de entorno y el `settings.py`.
- Los archivos de log se generan en la carpeta `logs/` (ignorados por Git).
- No se incluye ningún entorno virtual (`venv`) dentro del repositorio.
- Las dependencias en `requirements.txt` deben instalarse en un entorno virtual limpio para evitar conflictos con otros proyectos.

### Seguridad y manejo de secretos

El proyecto utiliza un `SECRET_KEY` por defecto para facilitar el desarrollo local y la evaluación académica. En el archivo `settings.py`, el `SECRET_KEY` se obtiene desde la variable de entorno `SECRET_KEY` si está definida; en caso contrario, se usa un valor por defecto válido para desarrollo.

**Importante**: En entornos de producción reales, el `SECRET_KEY` debe configurarse mediante variables de entorno y nunca debe versionarse en el repositorio. Para fines académicos y desarrollo local, el enfoque actual es aceptable.

### Feedback y colaboración

El repositorio permite el uso de Issues para reportar problemas o sugerencias. Las Discussions pueden utilizarse para ideas o mejoras futuras. Estas herramientas están disponibles como opción, no como requisito académico.

---

Este README está redactado para acompañar la evaluación académica y servir como referencia técnica básica para cualquier desarrollador que desee revisar o ejecutar el proyecto.
