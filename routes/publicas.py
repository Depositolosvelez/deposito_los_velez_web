from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from models import Producto, Cliente, slugify, grupos_con, GRUPOS_CATEGORIAS, CATEGORIA_NUEVA
from extensions import db

publicas_bp = Blueprint("publicas", __name__)

POR_PAGINA = 24
NEGOCIO = "Vélez Depósitos y Materiales"
RAZON_SOCIAL = "Depósitos de Recuperación de Materiales Los Vélez S.A.S."
NIT = "901.715.523-8"


@publicas_bp.app_template_filter("slugify")
def _slugify_filter(texto):
    return slugify(texto)


@publicas_bp.app_context_processor
def _datos_negocio():
    return {"RAZON_SOCIAL": RAZON_SOCIAL, "NIT": NIT}


def _categorias_existentes():
    return [r[0] for r in Producto.query.with_entities(Producto.categoria).distinct().all()]


def _url_imagen(p):
    if p.foto and p.foto.startswith("http"):
        return p.foto
    if p.foto:
        return url_for("static", filename="img/productos/" + p.foto, _external=True)
    return url_for("static", filename="img/logo_amarillo.png", _external=True)


def _oferta(p):
    """Offer / AggregateOffer de schema.org; None si el precio es a consultar."""
    base = {
        "priceCurrency": "COP",
        "availability": "https://schema.org/InStock",
        "itemCondition": "https://schema.org/" + ("NewCondition" if p.es_nuevo else "UsedCondition"),
        "url": url_for("publicas.producto", slug=p.slug, _external=True),
        "seller": {"@type": "LocalBusiness", "name": NEGOCIO, "telephone": "+573508494766"},
    }
    if p.unidad_medida == "UNIDAD_VARIABLE" and p.precio_min and p.precio_max:
        return {"@type": "AggregateOffer", "lowPrice": p.precio_min, "highPrice": p.precio_max, **base}
    if p.precio and p.precio > 0:
        return {"@type": "Offer", "price": int(p.precio), **base}
    return None


def _schema_producto(p):
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": p.nombre,
        "description": p.descripcion or p.descripcion_corta,
        "category": p.categoria,
        "image": _url_imagen(p),
        "url": url_for("publicas.producto", slug=p.slug, _external=True),
    }
    oferta = _oferta(p)
    if oferta:
        schema["offers"] = oferta
    return schema


def _render_catalogo(query, *, q="", categoria="", grupo="", url_pagina, **extra):
    page = request.args.get("page", 1, type=int)
    paginacion = query.order_by(Producto.nombre).paginate(page=page, per_page=POR_PAGINA, error_out=False)
    return render_template(
        "productos.html",
        productos=paginacion.items,
        paginacion=paginacion,
        grupos=grupos_con(_categorias_existentes()),
        categoria_activa=categoria,
        grupo_activo=grupo,
        q=q,
        total=paginacion.total,
        url_pagina=url_pagina,
        **extra,
    )


@publicas_bp.route("/")
def index():
    """Página de inicio"""
    return render_template("index.html", grupos=grupos_con(_categorias_existentes()))


@publicas_bp.route("/productos")
def productos():
    """Catálogo completo, búsqueda (q) y grupos de categorías (grupo)."""
    q         = request.args.get("q", "").strip()
    categoria = request.args.get("categoria", "").strip()
    grupo     = request.args.get("grupo", "").strip()

    # Los enlaces viejos ?categoria=X pasan a la página propia de la categoría
    if categoria and not q:
        return redirect(url_for("publicas.categoria", slug=slugify(categoria)), code=301)

    query = Producto.query
    if q:
        query = query.filter(db.or_(Producto.nombre.ilike(f"%{q}%"), Producto.descripcion.ilike(f"%{q}%")))
    if categoria:
        query = query.filter_by(categoria=categoria)
    elif grupo:
        cats = next((c for s, _, _, c in grupos_con(_categorias_existentes()) if s == grupo), None)
        if cats is None:
            return redirect(url_for("publicas.productos"))
        query = query.filter(Producto.categoria.in_(cats))

    return _render_catalogo(
        query, q=q, categoria=categoria, grupo=grupo,
        url_pagina=lambda n: url_for("publicas.productos", q=q or None, categoria=categoria or None,
                                     grupo=grupo or None, page=n),
    )


@publicas_bp.route("/categoria/<slug>")
def categoria(slug):
    cat = next((c for c in _categorias_existentes() if slugify(c) == slug), None)
    if cat is None:
        abort(404)
    grupo = next((s for s, _, _, cats in GRUPOS_CATEGORIAS if cat in cats), "varios")
    query = Producto.query.filter_by(categoria=cat)

    con_precio = [p.precio_min or p.precio for p in query.all() if (p.precio_min or p.precio)]
    nombre_legible = cat.capitalize()
    condicion = "" if cat == CATEGORIA_NUEVA else " de segunda"
    desde = f" desde {Producto._fmt(min(con_precio))} COP" if con_precio else ""
    meta_descripcion = (
        f"{nombre_legible}{condicion} en Montería, Córdoba{desde}. "
        "Precio negociable: consulta disponibilidad, medidas y estado por WhatsApp."
    )
    pagina = request.args.get("page", 1, type=int)
    return _render_catalogo(
        query, categoria=cat, grupo=grupo,
        url_pagina=lambda n: url_for("publicas.categoria", slug=slug, page=n if n > 1 else None),
        categoria_slug=slug,
        meta_descripcion=meta_descripcion,
        canonical=url_for("publicas.categoria", slug=slug, page=pagina if pagina > 1 else None, _external=True),
        schema_items=lambda productos: {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": f"{nombre_legible} — {NEGOCIO}",
            "itemListElement": [
                {"@type": "ListItem", "position": i, "item": _schema_producto(p)}
                for i, p in enumerate(productos, 1)
            ],
        },
    )


def _producto_por_slug(slug):
    return next((p for p in Producto.query.order_by(Producto.id).all() if p.slug == slug), None)


@publicas_bp.route("/producto/<slug>")
def producto(slug):
    """Página canónica de cada producto: /producto/puerta-de-hierro-frontal"""
    p = _producto_por_slug(slug)
    if p is None:
        abort(404)
    return render_template("producto_detalle.html", producto=p, schema=_schema_producto(p))


@publicas_bp.route("/productos/<int:id>")
@publicas_bp.route("/productos/<int:id>/<slug>")
def producto_legacy(id, slug=None):
    """URLs viejas con id — redirigen a /producto/<slug>."""
    p = Producto.query.get_or_404(id)
    return redirect(url_for("publicas.producto", slug=p.slug), code=301)


def _falta_autorizacion():
    if request.form.get("autoriza_datos") != "si":
        flash("Debes autorizar el tratamiento de tus datos personales para enviarnos tu consulta.", "danger")
        return True
    return False


@publicas_bp.route("/contacto", methods=["GET", "POST"])
def contacto():
    """Página de contacto — guarda el lead en la BD y redirige a /gracias"""
    if request.method == "POST":
        nombre   = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        mensaje  = request.form.get("mensaje", "").strip()
        fuente   = request.form.get("fuente", "Web").strip()

        errores = []
        if not nombre:
            errores.append("El nombre es obligatorio.")
        if not telefono:
            errores.append("El teléfono es obligatorio.")
        if not mensaje:
            errores.append("El mensaje no puede estar vacío.")

        if errores:
            for error in errores:
                flash(error, "danger")
            return redirect(url_for("publicas.contacto"))
        if _falta_autorizacion():
            return redirect(url_for("publicas.contacto"))

        cliente = Cliente(
            nombre=nombre,
            telefono=telefono,
            notas=mensaje,
            fuente=fuente,
            estado="Interesado",
        )
        db.session.add(cliente)
        db.session.commit()
        return redirect(url_for("publicas.gracias"))

    return render_template("contacto.html")


@publicas_bp.route("/gracias")
def gracias():
    return render_template("gracias.html")


@publicas_bp.route("/cotizar", methods=["POST"])
def cotizar():
    nombre   = request.form.get("nombre", "").strip()
    telefono = request.form.get("telefono", "").strip()
    mensaje  = request.form.get("mensaje", "").strip() or "Cotización solicitada"
    fuente   = request.form.get("fuente", "Web").strip()
    if not nombre or not telefono or _falta_autorizacion():
        return redirect(url_for("publicas.contacto"))
    db.session.add(Cliente(
        nombre=nombre, telefono=telefono, notas=mensaje,
        fuente=fuente, estado="Interesado",
    ))
    db.session.commit()
    return redirect(url_for("publicas.gracias"))


@publicas_bp.route("/preguntas-frecuentes")
def preguntas_frecuentes():
    return render_template("preguntas_frecuentes.html")


@publicas_bp.route("/privacidad")
def privacidad():
    return render_template("privacidad.html")


@publicas_bp.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template("404.html"), 404


@publicas_bp.errorhandler(500)
def error_interno(e):
    return render_template("500.html"), 500
