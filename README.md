Kalué Beauty Store

Tienda online de maquillaje con panel de administración completo.
Desarrollada con Django + PostgreSQL + Cloudinary.

---

Vista pública

- Catálogo de productos con filtros por categoría y subcategoría
- Buscador en tiempo real
- Página de detalle por producto con galería de fotos
- Selector de variantes (colores/tonos) con precio dinámico
- Botón de WhatsApp directo con el producto seleccionado

Panel de administración

Acceso en `/dashboard/login/`

### Roles
| Rol | Permisos |
|-----|----------|
| Administrador | Todo — productos, stock, ventas, gastos, historial |
| Vendedor | Ver productos, registrar ventas |

Funciones
- Gestión de productos con variantes e imágenes (Cloudinary)
- Control de stock por lotes de compra
- Registro de ventas con descuentos
- Historial de movimientos de stock
- Gastos extras (envíos, bolsas, regalos)
- Resumen financiero: ingresos, costos, gastos y ganancia real

---

Tecnologías

| Tecnología | Uso |
|------------|-----|
| Python / Django | Backend |
| PostgreSQL | Base de datos |
| Cloudinary | Almacenamiento de imágenes |
| Whitenoise | Archivos estáticos en producción |
| Gunicorn | Servidor WSGI |
| Render | Hosting |
| HTML / CSS / JS | Frontend |

---

Instalación local

Requisitos
- Python 3.10+
- pip

Pasos

```bash
# 1. Clona el repositorio
git clone https://github.com/tu_usuario/kalue-django.git
cd kalue-django

# 2. Crea el entorno virtual
python -m venv venv

# 3. Actívalo
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Instala dependencias
pip install -r requirements.txt

# 5. Crea el archivo .env
cp .env.example .env
# Edita .env con tus credenciales

# 6. Crea las tablas
python manage.py migrate

# 7. Crea el superusuario
python manage.py createsuperuser

# 8. Corre el servidor
python manage.py runserver
```

---

Variables de entorno

Crea un archivo `.env` en la raíz del proyecto:
