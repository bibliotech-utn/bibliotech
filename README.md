## BiblioTech – Sistema de Gestión de Biblioteca

BiblioTech es un sistema de gestión de biblioteca desarrollado como proyecto académico utilizando Django y Python.  
Permite administrar libros, ejemplares, socios, personal y préstamos, con una interfaz web pensada para uso en instituciones educativas.

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
git clone <URL_DEL_REPOSITORIO>
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

Su uso no es obligatorio. Para la evaluación académica es suficiente seguir los pasos manuales indicados en las secciones de instalación y ejecución.

---

## Estructura general del proyecto

Estructura simplificada de los elementos principales:

```text
.
├── bibliotech.py              # Script opcional de automatización (desarrollo)
├── requirements.txt           # Dependencias de Python
├── README.md                  # Documentación principal del proyecto
└── biblioteca/
    ├── manage.py              # Punto de entrada de Django
    ├── biblioteca/            # Configuración del proyecto
    │   ├── settings.py
    │   ├── urls.py
    │   ├── views.py
    │   └── ...
    ├── gestion_autores/       # App: autores
    ├── gestion_libros/        # App: libros y ejemplares
    ├── gestion_socios/        # App: socios
    ├── gestion_personal/      # App: personal de biblioteca
    ├── gestion_prestamos/     # App: préstamos y reservas
    ├── gestion_importaciones/ # App: historial de importaciones
    ├── templates/             # Templates HTML (base y módulos)
    └── static/                # Recursos estáticos (CSS adicionales)
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

## Roles del equipo

El proyecto fue desarrollado en equipo como trabajo académico para la UTN FRLP.  
Los créditos se encuentran también en el pie de página de la aplicación (templates).

- **Integrantes**: Stella Cáceres, Juan Zunino y Ramiro Quevedo.

---

## Notas técnicas y consideraciones

- El proyecto está pensado para ejecutarse en entorno de desarrollo con SQLite.  
  Para despliegues en producción se pueden utilizar otras bases de datos configurando las variables de entorno y el `settings.py`.
- Los archivos de log se generan en la carpeta `logs/` (ignorados por Git).
- No se incluye ningún entorno virtual (`venv`) dentro del repositorio.
- Las dependencias en `requirements.txt` deben instalarse en un entorno virtual limpio para evitar conflictos con otros proyectos.

Este README está redactado para acompañar la evaluación académica y servir como referencia técnica básica para cualquier desarrollador que desee revisar o ejecutar el proyecto.
