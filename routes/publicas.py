import urllib.parse
from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import Producto, Cliente
from extensions import db

publicas_bp = Blueprint("publicas", __name__)


@publicas_bp.route("/")
def index():
    """Página de inicio"""
    return render_template("index.html")


@publicas_bp.route("/productos")
def productos():
    """Catálogo de productos — carga desde la base de datos"""
    q         = request.args.get("q", "").strip()
    categoria = request.args.get("categoria", "").strip()

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

    lista      = query.order_by(Producto.nombre).all()
    categorias = [r[0] for r in Producto.query.with_entities(Producto.categoria).distinct().all()]
    return render_template("productos.html", productos=lista, categorias=categorias,
                           categoria_activa=categoria, q=q)


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


@publicas_bp.route("/productos/<int:id>")
def producto_detalle(id):
    producto = Producto.query.get_or_404(id)
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
