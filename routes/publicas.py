import urllib.parse
from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import Producto

publicas_bp = Blueprint("publicas", __name__)


@publicas_bp.route("/")
def index():
    """Página de inicio"""
    return render_template("index.html")


@publicas_bp.route("/productos")
def productos():
    """Catálogo de productos — carga desde la base de datos"""
    categoria = request.args.get("categoria", "")
    if categoria:
        lista = Producto.query.filter_by(categoria=categoria).all()
    else:
        lista = Producto.query.all()

    categorias = [r[0] for r in Producto.query.with_entities(Producto.categoria).distinct().all()]
    return render_template("productos.html", productos=lista, categorias=categorias, categoria_activa=categoria)


@publicas_bp.route("/contacto", methods=["GET", "POST"])
def contacto():
    """Página de contacto con validación y redirección a WhatsApp"""
    if request.method == "POST":
        nombre  = request.form.get("nombre", "").strip()
        email   = request.form.get("email", "").strip()
        mensaje = request.form.get("mensaje", "").strip()

        errores = []
        if not nombre:
            errores.append("El nombre es obligatorio.")
        if not email or "@" not in email:
            errores.append("Ingresa un email válido.")
        if not mensaje:
            errores.append("El mensaje no puede estar vacío.")

        if errores:
            for error in errores:
                flash(error, "danger")
            return redirect(url_for("publicas.contacto"))

        texto = f"Hola, soy {nombre} ({email}). {mensaje}"
        texto_codificado = urllib.parse.quote(texto)
        whatsapp_url = f"https://wa.me/57TUNUMERO?text={texto_codificado}"
        return redirect(whatsapp_url)

    return render_template("contacto.html")


@publicas_bp.route("/privacidad")
def privacidad():
    return render_template("privacidad.html")


@publicas_bp.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template("404.html"), 404


@publicas_bp.errorhandler(500)
def error_interno(e):
    return render_template("500.html"), 500
