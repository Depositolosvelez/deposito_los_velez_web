from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import Producto, Cliente, slugify
from extensions import db

publicas_bp = Blueprint("publicas", __name__)

POR_PAGINA = 24


@publicas_bp.route("/")
def index():
    return render_template("index.html")


@publicas_bp.route("/productos")
def productos():
    q         = request.args.get("q", "").strip()
    categoria = request.args.get("categoria", "").strip()
    page      = request.args.get("page", 1, type=int)

    query = Producto.query
    if q:
        query = query.filter(
            db.or_(
                Producto.nombre.ilike(f"%{q}%"),
                Producto.descripcion.ilike(f"%{q}%")
            )
        )
    if categoria:
        query = query.filter_by(categoria=categoria)

    paginacion = query.order_by(Producto.nombre).paginate(
        page=page, per_page=POR_PAGINA, error_out=False
    )
    categorias = [r[0] for r in Producto.query.with_entities(Producto.categoria).distinct().all()]
    return render_template(
        "productos.html",
        productos=paginacion.items,
        paginacion=paginacion,
        categorias=categorias,
        categoria_activa=categoria,
        q=q,
        total=paginacion.total,
    )


@publicas_bp.route("/contacto", methods=["GET", "POST"])
def contacto():
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

        db.session.add(Cliente(
            nombre=nombre, telefono=telefono, notas=mensaje,
            fuente=fuente, estado="Interesado",
        ))
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
    if not nombre or not telefono:
        return redirect(url_for("publicas.contacto"))
    db.session.add(Cliente(
        nombre=nombre, telefono=telefono, notas=mensaje,
        fuente=fuente, estado="Interesado",
    ))
    db.session.commit()
    return redirect(url_for("publicas.gracias"))


@publicas_bp.route("/productos/<int:id>")
def producto_detalle(id):
    """Ruta legacy — redirige a la URL canónica con slug."""
    producto = Producto.query.get_or_404(id)
    return redirect(
        url_for("publicas.producto_detalle_slug", id=id, slug=producto.slug),
        code=301
    )


@publicas_bp.route("/productos/<int:id>/<slug>")
def producto_detalle_slug(id, slug):
    """URL canónica SEO-friendly: /productos/12/puerta-de-hierro-frontal"""
    producto = Producto.query.get_or_404(id)
    # Si el slug no coincide redirige al correcto (previene duplicados)
    if slug != producto.slug:
        return redirect(
            url_for("publicas.producto_detalle_slug", id=id, slug=producto.slug),
            code=301
        )
    return render_template("producto_detalle.html", producto=producto)


@publicas_bp.route("/privacidad")
def privacidad():
    return render_template("privacidad.html")


@publicas_bp.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template("404.html"), 404


@publicas_bp.errorhandler(500)
def error_interno(e):
    return render_template("500.html"), 500
