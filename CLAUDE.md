# CLAUDE.md — Depósito Los Vélez Web

## Negocio

**Nombre:** Vélez Depósitos y Materiales  
**Rubro:** Comercio de materiales de construcción de segunda mano  
**Ubicación:** Montería, Córdoba, Colombia (Barrio Cantaclaro, diagonal a urgencias CAMU Viejo)  
**Propuesta de valor:** Materiales de demolición a precios 40–70% más bajos que nuevos  
**Modelo:** E-commerce B2C con cierre de venta vía WhatsApp (+57 350 849 4766)  
**Horario:** Lunes a Sábado, 8am – 6pm  
**Email:** depositolosvelez@gmail.com  
**Sitio en producción:** https://velezdepositos.com.co  
**Panel admin:** https://velezdepositos.com.co/admin  

---

## Stack técnico

| Capa | Tecnología |
|------|-----------|
| Framework | Flask 3.1.2 (Python) |
| ORM | SQLAlchemy 2.0.36 vía Flask-SQLAlchemy |
| DB dev | SQLite (`deposito.db`) |
| DB prod | PostgreSQL (`DATABASE_URL` en `.env`) |
| Frontend | Bootstrap 5.3.2 + Jinja2 templates |
| Imágenes | Cloudinary (fallback: `static/img/productos/`) |
| Servidor | Gunicorn (producción) |

**Dependencias clave:** `flask`, `flask-sqlalchemy`, `gunicorn`, `python-dotenv`, `psycopg2-binary`, `cloudinary`

---

## Estructura de directorios

```
deposito_los_velez_web/        ← raíz del repo
└── deposito_los_velez_web/    ← paquete Python (app real)
    ├── app.py                 ← factory pattern, registra blueprints
    ├── extensions.py          ← inicializa db = SQLAlchemy()
    ├── models.py              ← Producto, Cliente
    ├── requirements.txt
    ├── routes/
    │   ├── publicas.py        ← catálogo, contacto, cotizar, privacidad
    │   ├── admin.py           ← CRUD productos, login/logout
    │   ├── clientes.py        ← CRM: lista, form, estadísticas, CSV export
    │   └── sitemap.py         ← /robots.txt, /sitemap.xml
    ├── templates/
    │   ├── base.html          ← layout + navbar + footer + popups + WhatsApp btn
    │   ├── index.html         ← hero, categorías, testimonios, CTA
    │   ├── productos.html     ← catálogo con filtros dinámicos por grupo
    │   ├── producto_detalle.html
    │   ├── contacto.html      ← formulario + mapa Google
    │   ├── gracias.html
    │   ├── privacidad.html
    │   └── admin/
    │       ├── login.html
    │       ├── lista.html
    │       ├── formulario.html
    │       ├── sin_imagen.html
    │       └── clientes/
    │           ├── lista.html
    │           ├── form.html
    │           ├── seguimiento.html
    │           └── estadisticas.html
    └── static/
        ├── css/style.css      ← vars: #080a0f (fondo), #D4AF37 (dorado)
        ├── fonts/
        └── img/
            ├── logo_amarillo.png
            ├── whatsapp_icon.png
            ├── [categoria].png  ← imágenes por categoría
            └── productos/       ← fotos locales (UUID.jpg)
```

---

## Modelos de datos

### Producto
```python
id          : Integer PK
nombre      : String(120)   # "Puerta de hierro frontal"
precio      : Float          # COP, 0 = consultar
categoria   : String(80)    # ver lista de categorías abajo
descripcion : Text           # default: "Consultar precio. Material de segunda en buen estado."
foto        : String(200)   # URL Cloudinary o nombre archivo local
```

### Cliente (CRM)
```python
id               : Integer PK
nombre           : String(100)
telefono         : String(20)
ciudad           : String(100)
producto_interes : String(200)
estado           : String(50)   # "Interesado" | "Compró" | "Seguimiento" | "Frío"
fuente           : String(50)   # "Web" | "WhatsApp" | "Facebook" | "Google Ads" | "Popup Entrada" | "Popup Salida"
notas            : Text
fecha_registro   : DateTime
```

---

## Rutas principales

### Públicas (`routes/publicas.py`)
- `GET /` — inicio
- `GET /productos` — catálogo (params: `q`, `categoria`)
- `GET /productos/<id>` — detalle
- `GET|POST /contacto` — formulario → crea Cliente
- `POST /cotizar` — popup cotización → crea Cliente
- `GET /gracias` — confirmación post-contacto
- `GET /privacidad`

### Admin (`routes/admin.py`) — requiere login
- `GET|POST /admin/login` — rate limit: 5 intentos, bloqueo 15 min
- `GET /admin/` — listado productos
- `GET|POST /admin/agregar`
- `GET|POST /admin/editar/<id>`
- `POST /admin/eliminar/<id>`
- `GET /admin/sin-imagen` — reporte

### CRM (`routes/clientes.py`) — requiere login
- `GET /admin/clientes` — listado filtrable
- `GET|POST /admin/clientes/nuevo`
- `GET|POST /admin/clientes/<id>/editar`
- `POST /admin/clientes/eliminar/<id>`
- `GET /admin/clientes/exportar` — CSV
- `GET /admin/clientes/seguimiento` — hot leads con link WhatsApp preformateado
- `GET /admin/clientes/estadisticas` — dashboard métricas

---

## Categorías de productos (30+)

BAÑOS Y SANITARIOS, PUERTAS, REJAS Y PROTECTORES, VENTANAS, TECHOS Y CUBIERTAS, TUBERÍA PVC, ACCESORIOS PVC, TUBERÍA HIERRO GALVANIZADO, CABLE ELÉCTRICO, GUAYAS EN ALUMINIO, GUAYAS EN ACERO, SEGURIDAD Y ALTURA, HERRAMIENTA Y FERRETERÍA, ESCALERAS ESTRUCTURALES, ESCALERAS DE ALUMINIO, MAQUINARIA Y EQUIPOS, TRANSFORMADORES, COCINA, HORNOS, LAVAPLATOS, MALLAS, HERRAJE ELÉCTRICO, VARIOS

---

## Variables de entorno (`.env`)

```
SECRET_KEY=
DEBUG=false
DATABASE_URL=postgresql://user:pass@localhost/deposito
ADMIN_USER=
ADMIN_PASSWORD=
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

---

## Seguridad implementada

- Headers: `X-Content-Type-Options`, `X-Frame-Options: DENY`, `X-XSS-Protection`
- Login admin con rate limiting por IP (5 intentos → bloqueo 15 min)
- Validación de archivos: solo PNG/JPG/JPEG/WEBP, máx 10 MB, nombre UUID
- CSRF vía Flask session

---

## Funcionalidades de marketing

- **Popup entrada** (8 seg): captura nombre + teléfono → Cliente con `fuente="Popup Entrada"`
- **Popup salida** (exit intent): segunda oportunidad antes de cerrar pestaña
- **Detección UTM:** detecta automáticamente parámetros de Google Ads y Facebook
- **Botón WhatsApp flotante** (derecha) + **Chat flotante** (izquierda, expandible)
- **Top bar cerrable:** anuncio dorado ("Respondemos en 1 hora")
- **Google Ads conversion tracking:** ID `AW-18188659080`
- **SEO:** sitemap.xml dinámico, robots.txt, meta descriptions por página, OpenGraph

---

## Flujos de negocio clave

1. **Visita → Lead:** usuario llega → popup 8s → llena teléfono → `/gracias` → Cliente guardado
2. **Catálogo → WhatsApp:** filtra/busca → detalle → botón WhatsApp → enlace `wa.me/573508494766?text=...`
3. **Admin CRUD:** login → lista → agregar (imagen a Cloudinary) → producto visible en catálogo
4. **CRM:** clientes llegan por web → admin filtra por estado → click teléfono → WhatsApp preformateado → actualiza estado

---

## Estilo y diseño

### Paleta de colores exacta
| Variable | Hex | Uso |
|----------|-----|-----|
| Fondo principal | `#080a0f` | `background-color` del body y secciones oscuras |
| Dorado acento | `#D4AF37` | botones, precios, badges, bordes activos |
| Amarillo logo | `#fdcb17` | color exclusivo del logo en navbar y hero |
| Texto principal | `#ffffff` | texto sobre fondos oscuros |

**Regla crítica:** no introducir colores nuevos sin aprobación. Cualquier cambio de color debe usar estas variables o extenderlas en `style.css`.

### Tipografías
- **Orbitron** — usada en el hero (títulos principales, slogan). No reemplazar ni cambiar peso/tamaño sin aprobación.
- **Nasalization** — tipografía de marca (nombre "Los Vélez", identidad). No tocar bajo ninguna circunstancia.

**Regla crítica:** nunca cambiar ni sobreescribir las tipografías Orbitron y Nasalization.

### Otros elementos visuales
- **Framework CSS:** Bootstrap 5.3.2 vía CDN + `static/css/style.css`
- **Logo principal:** `static/img/logo_amarillo.png`
- **Cards productos:** hover lift, badge categoría, precio en dorado, botón WhatsApp verde
- **Filtros catálogo:** grupos expandibles con animación fadeDown 200ms (JavaScript vanilla)

---

## Convenciones de desarrollo

- Blueprints Flask para cada módulo (no poner rutas en `app.py`)
- `extensions.py` es la única fuente de `db`; importar desde ahí, nunca redefinir
- Imágenes: subir a Cloudinary si está configurado, guardar URL; si no, guardar en `static/img/productos/` con nombre UUID
- Precios en COP (pesos colombianos); precio `0` significa "consultar"
- No agregar comentarios innecesarios al código — solo cuando el "por qué" no sea obvio
- No crear abstracciones anticipadas; resolver el problema puntual

### Reglas obligatorias

1. **Idioma:** responder siempre en español, sin excepción.
2. **Tipografías:** nunca modificar Orbitron ni Nasalization — ni familia, ni peso, ni tamaño.
3. **Estilos:** no romper estilos existentes; cualquier cambio CSS debe ser aditivo y probado visualmente.
4. **Git:** hacer push a GitHub después de cada cambio importante (feature completa, corrección relevante). No acumular cambios sin pushear.

### Credenciales admin local (desarrollo)

```
Usuario: admin
Contraseña: deposito2025
URL: http://localhost:5000/admin/login
```

### Productos estrella (más consultados y vendidos)

Priorizar visibilidad, fotos de calidad y descripciones detalladas para:
- **Puertas de hierro** — producto más consultado, alto ticket
- **Sanitarios** (inodoros, lavamanos) — alta rotación
- **Cables de cobre** — búsqueda frecuente, categoría CABLE ELÉCTRICO
- **Rejas** — categoría REJAS Y PROTECTORES, demanda constante

---

## Integraciones externas

| Servicio | Uso |
|----------|-----|
| Cloudinary | Almacenamiento imágenes productos |
| Google Maps | Embed en `/contacto` |
| WhatsApp Web API | Links `wa.me/` en productos y CRM |
| Google Ads | Conversion tracking `AW-18188659080` |
| Bootstrap CDN | CSS + Icons |
