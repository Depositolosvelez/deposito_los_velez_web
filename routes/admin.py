import os
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
from extensions import db
from models import Producto

admin_bp = Blueprint("admin", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _cloudinary_configured():
    return all([
        os.environ.get("CLOUDINARY_CLOUD_NAME"),
        os.environ.get("CLOUDINARY_API_KEY"),
        os.environ.get("CLOUDINARY_API_SECRET"),
    ])


def guardar_imagen(file_storage):
    """
    Sube la imagen a Cloudinary si está configurado, o la guarda localmente.
    Devuelve la URL de Cloudinary (str) o el nombre de archivo local (str).
    """
    if _cloudinary_configured():
        import cloudinary
        import cloudinary.uploader
        cloudinary.config(
            cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
            api_key=os.environ.get("CLOUDINARY_API_KEY"),
            api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
            secure=True,
        )
        result = cloudinary.uploader.upload(
            file_storage,
            folder="deposito_los_velez",
            resource_type="image",
        )
        return result["secure_url"]
    else:
        # Fallback: guardar localmente
        upload_folder = os.path.join(current_app.root_path, "static", "img", "productos")
        os.makedirs(upload_folder, exist_ok=True)
        ext = secure_filename(file_storage.filename).rsplit(".", 1)[1].lower()
        nombre = f"{uuid.uuid4().hex}.{ext}"
        file_storage.save(os.path.join(upload_folder, nombre))
        return nombre


# Rastreo de intentos de login por IP {ip: {"count": n, "blocked_until": datetime|None}}
_login_attempts: dict = {}


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
MAX_INTENTOS  = 5
BLOQUEO_MIN   = 15

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ip = request.remote_addr
        ahora = datetime.now()
        datos = _login_attempts.get(ip, {"count": 0, "blocked_until": None})

        # Verificar bloqueo activo
        if datos["blocked_until"] and ahora < datos["blocked_until"]:
            minutos = int((datos["blocked_until"] - ahora).seconds / 60) + 1
            flash(f"Demasiados intentos. Intenta en {minutos} minuto{'s' if minutos != 1 else ''}.", "danger")
            return render_template("admin/login.html")

        usuario    = request.form.get("usuario", "")
        password   = request.form.get("password", "")
        admin_user = os.environ.get("ADMIN_USER", "admin")
        admin_pass = os.environ.get("ADMIN_PASSWORD", "Velez2026$#")

        if usuario == admin_user and password == admin_pass:
            _login_attempts.pop(ip, None)
            session["admin_logueado"] = True
            return redirect(url_for("admin.lista"))
        else:
            datos["count"] += 1
            if datos["count"] >= MAX_INTENTOS:
                datos["blocked_until"] = ahora + timedelta(minutes=BLOQUEO_MIN)
                datos["count"] = 0
                flash(f"Demasiados intentos. Intenta en {BLOQUEO_MIN} minutos.", "danger")
            else:
                restantes = MAX_INTENTOS - datos["count"]
                flash(f"Usuario o contraseña incorrectos. Intentos restantes: {restantes}.", "danger")
            _login_attempts[ip] = datos

    return render_template("admin/login.html")


@admin_bp.route("/logout")
def logout():
    session.pop("admin_logueado", None)
    return redirect(url_for("admin.login"))


# ================= LISTAR PRODUCTOS =================
@admin_bp.route("/")
@login_requerido
def lista():
    q   = request.args.get("q", "").strip()
    cat = request.args.get("cat", "").strip()

    query = Producto.query
    if q:
        query = query.filter(
            db.or_(
                Producto.nombre.ilike(f"%{q}%"),
                Producto.descripcion.ilike(f"%{q}%")
            )
        )
    if cat:
        query = query.filter(Producto.categoria == cat)

    productos   = query.order_by(Producto.nombre).all()
    categorias  = db.session.query(Producto.categoria).distinct().order_by(Producto.categoria).all()
    categorias  = [c[0] for c in categorias]

    return render_template("admin/lista.html",
                           productos=productos,
                           categorias=categorias,
                           q=q,
                           cat=cat)


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

        nombre_foto = None
        if foto and foto.filename:
            if not allowed_file(foto.filename):
                flash("Formato no permitido. Usa JPG, PNG o WEBP.", "danger")
                return redirect(url_for("admin.agregar"))
            try:
                nombre_foto = guardar_imagen(foto)
            except Exception as e:
                flash(f"Error al subir la imagen: {e}", "danger")
                return redirect(url_for("admin.agregar"))

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
        if foto and foto.filename:
            if not allowed_file(foto.filename):
                flash("Formato no permitido. Usa JPG, PNG o WEBP.", "danger")
                return redirect(url_for("admin.editar", id=id))
            try:
                producto.foto = guardar_imagen(foto)
            except Exception as e:
                flash(f"Error al subir la imagen: {e}", "danger")
                return redirect(url_for("admin.editar", id=id))

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
