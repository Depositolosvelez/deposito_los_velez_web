import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from extensions import db
from models import Producto

admin_bp = Blueprint("admin", __name__)

UPLOAD_FOLDER   = os.path.join("static", "img", "productos")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def login_requerido(f):
    """Decorador simple para proteger rutas del admin"""
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logueado"):
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return wrapper


# ================= LOGIN =================
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario  = request.form.get("usuario", "")
        password = request.form.get("password", "")
        admin_user = os.environ.get("ADMIN_USER", "admin")
        admin_pass = os.environ.get("ADMIN_PASSWORD", "admin123")

        if usuario == admin_user and password == admin_pass:
            session["admin_logueado"] = True
            return redirect(url_for("admin.lista"))
        else:
            flash("Usuario o contraseña incorrectos.", "danger")

    return render_template("admin/login.html")


@admin_bp.route("/logout")
def logout():
    session.pop("admin_logueado", None)
    return redirect(url_for("admin.login"))


# ================= LISTAR PRODUCTOS =================
@admin_bp.route("/")
@login_requerido
def lista():
    productos = Producto.query.all()
    return render_template("admin/lista.html", productos=productos)


# ================= AGREGAR PRODUCTO =================
@admin_bp.route("/agregar", methods=["GET", "POST"])
@login_requerido
def agregar():
    if request.method == "POST":
        nombre      = request.form.get("nombre", "").strip()
        precio      = request.form.get("precio", "0").strip()
        categoria   = request.form.get("categoria", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        foto        = request.files.get("foto")

        # Validación
        errores = []
        if not nombre:
            errores.append("El nombre es obligatorio.")
        try:
            precio = float(precio)
        except ValueError:
            errores.append("El precio debe ser un número.")
        if not categoria:
            errores.append("La categoría es obligatoria.")

        if errores:
            for e in errores:
                flash(e, "danger")
            return redirect(url_for("admin.agregar"))

        # Guardar foto
        nombre_foto = None
        if foto and allowed_file(foto.filename):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            nombre_foto = secure_filename(foto.filename)
            foto.save(os.path.join(UPLOAD_FOLDER, nombre_foto))

        # Guardar en BD
        nuevo = Producto(
            nombre=nombre,
            precio=precio,
            categoria=categoria,
            descripcion=descripcion,
            foto=nombre_foto
        )
        db.session.add(nuevo)
        db.session.commit()
        flash(f"Producto '{nombre}' agregado correctamente.", "success")
        return redirect(url_for("admin.lista"))

    return render_template("admin/formulario.html", producto=None)


# ================= EDITAR PRODUCTO =================
@admin_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@login_requerido
def editar(id):
    producto = Producto.query.get_or_404(id)

    if request.method == "POST":
        producto.nombre      = request.form.get("nombre", "").strip()
        producto.categoria   = request.form.get("categoria", "").strip()
        producto.descripcion = request.form.get("descripcion", "").strip()
        try:
            producto.precio = float(request.form.get("precio", "0"))
        except ValueError:
            flash("El precio debe ser un número.", "danger")
            return redirect(url_for("admin.editar", id=id))

        foto = request.files.get("foto")
        if foto and allowed_file(foto.filename):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            nombre_foto = secure_filename(foto.filename)
            foto.save(os.path.join(UPLOAD_FOLDER, nombre_foto))
            producto.foto = nombre_foto

        db.session.commit()
        flash(f"Producto '{producto.nombre}' actualizado.", "success")
        return redirect(url_for("admin.lista"))

    return render_template("admin/formulario.html", producto=producto)


# ================= ELIMINAR PRODUCTO =================
@admin_bp.route("/eliminar/<int:id>", methods=["POST"])
@login_requerido
def eliminar(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash(f"Producto '{producto.nombre}' eliminado.", "success")
    return redirect(url_for("admin.lista"))
