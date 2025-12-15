## BiblioTech – Sistema de Gestión de Biblioteca

BiblioTech es un sistema de gestión de biblioteca desarrollado como proyecto académico utilizando Django y Python.  
Permite administrar libros, ejemplares, socios, personal y préstamos, con una interfaz web pensada para uso en instituciones educativas.

**Repositorio público oficial**: https://github.com/bibliotech-utn/bibliotech  
El repositorio forma parte de la organización del grupo de trabajo.

---

## Objetivo del sistema

- **Administrar el catálogo** de libros y ejemplares de una biblioteca.
- **Registrar y controlar préstamos** y devoluciones, incluyendo estados y vencimientos.
- **Gestionar socios y personal**, diferenciando sus permisos y vistas.
- **Facilitar tareas operativas** (búsquedas, filtros, exportación a CSV e importación desde Excel).

---

## Landing y presentación del proyecto

El sistema incluye dos vistas institucionales accesibles desde el servidor de desarrollo, pensadas para contextualizar el proyecto y facilitar su presentación académica:

- **Landing page institucional**  
  URL: `http://127.0.0.1:8000/landing/`  
  Página de introducción general al sistema. Presenta BiblioTech de forma resumida y orientada a la primera impresión, explicando el propósito del proyecto y su contexto de uso.

- **Presentación del sistema**  
  URL: `http://127.0.0.1:8000/presentacion/`  
  Vista explicativa que describe el funcionamiento del sistema, sus módulos principales y el enfoque adoptado en el desarrollo del proyecto.

Ambas vistas están implementadas como templates HTML y se encuentran disponibles una vez que el servidor de desarrollo está en ejecución.

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
- Entorno virtual de Python (recomendado).

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/bibliotech-utn/bibliotech.git
cd bibliotech
