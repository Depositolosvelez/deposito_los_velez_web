import csv
import io
from datetime import date, datetime, timedelta
from functools import wraps
from urllib.parse import quote as url_quote
from sqlalchemy import func
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response
from extensions import db
from models import Cliente

clientes_bp = Blueprint("clientes", __name__)

ESTADOS  = ["Interesado", "Compró", "Seguimiento", "Frío"]
FUENTES  = ["WhatsApp", "Referido", "Walk-in", "Web", "Facebook", "Otro"]


def login_requerido(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logueado"):
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return wrapper


@clientes_bp.route("/clientes")
@login_requerido
def lista():
    estado = request.args.get("estado", "")
    ciudad = request.args.get("ciudad", "")

    query = Cliente.query
    if estado:
        query = query.filter_by(estado=estado)
    if ciudad:
        query = query.filter(Cliente.ciudad.ilike(f"%{ciudad}%"))

    clientes = query.order_by(Cliente.fecha_registro.desc()).all()
    ciudades = [r[0] for r in Cliente.query.with_entities(Cliente.ciudad).distinct().all() if r[0]]

    return render_template(
        "admin/clientes/lista.html",
        clientes=clientes,
        estados=ESTADOS,
        ciudades=ciudades,
        filtro_estado=estado,
        filtro_ciudad=ciudad,
    )


@clientes_bp.route("/clientes/nuevo", methods=["GET", "POST"])
@login_requerido
def nuevo():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        if not nombre:
            flash("El nombre es obligatorio.", "danger")
            return redirect(url_for("clientes.nuevo"))

        cliente = Cliente(
            nombre=nombre,
            telefono=request.form.get("telefono", "").strip(),
            ciudad=request.form.get("ciudad", "").strip(),
            producto_interes=request.form.get("producto_interes", "").strip(),
            estado=request.form.get("estado", "Interesado").strip(),
            fuente=request.form.get("fuente", "Walk-in").strip(),
            notas=request.form.get("notas", "").strip(),
        )
        db.session.add(cliente)
        db.session.commit()
        flash(f"Cliente '{nombre}' agregado correctamente.", "success")
        return redirect(url_for("clientes.lista"))

    return render_template("admin/clientes/form.html", cliente=None, estados=ESTADOS, fuentes=FUENTES)


@clientes_bp.route("/clientes/<int:id>/editar", methods=["GET", "POST"])
@login_requerido
def editar(id):
    cliente = Cliente.query.get_or_404(id)

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        if not nombre:
            flash("El nombre es obligatorio.", "danger")
            return redirect(url_for("clientes.editar", id=id))

        cliente.nombre = nombre
        cliente.telefono = request.form.get("telefono", "").strip()
        cliente.ciudad = request.form.get("ciudad", "").strip()
        cliente.producto_interes = request.form.get("producto_interes", "").strip()
        cliente.estado = request.form.get("estado", "Interesado").strip()
        cliente.fuente = request.form.get("fuente", "Walk-in").strip()
        cliente.notas = request.form.get("notas", "").strip()

        db.session.commit()
        flash(f"Cliente '{cliente.nombre}' actualizado.", "success")
        return redirect(url_for("clientes.lista"))

    return render_template("admin/clientes/form.html", cliente=cliente, estados=ESTADOS, fuentes=FUENTES)


@clientes_bp.route("/clientes/exportar")
@login_requerido
def exportar():
    clientes = Cliente.query.order_by(Cliente.fecha_registro.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["nombre", "telefono", "ciudad", "producto_interes", "estado", "notas", "fecha_registro"])
    for c in clientes:
        writer.writerow([
            c.nombre,
            c.telefono or "",
            c.ciudad or "",
            c.producto_interes or "",
            c.estado,
            c.notas or "",
            c.fecha_registro.strftime("%Y-%m-%d %H:%M") if c.fecha_registro else "",
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=clientes.csv"},
    )


def _wa_seguimiento_url(cliente):
    if not cliente.telefono:
        return None
    tel  = cliente.telefono.replace(" ", "").replace("-", "")
    prod = cliente.producto_interes or "nuestros productos"
    msg  = f"Hola {cliente.nombre}, le contactamos del Depósito Los Vélez. ¿Sigue interesado en {prod}?"
    return f"https://wa.me/57{tel}?text={url_quote(msg)}"


@clientes_bp.route("/clientes/seguimiento")
@login_requerido
def seguimiento():
    clientes = Cliente.query.filter(
        Cliente.estado.in_(["Interesado", "Seguimiento"])
    ).order_by(Cliente.fecha_registro.asc()).all()
    hoy     = date.today()
    wa_urls = {c.id: _wa_seguimiento_url(c) for c in clientes}
    return render_template(
        "admin/clientes/seguimiento.html",
        clientes=clientes,
        hoy=hoy,
        wa_urls=wa_urls,
    )


@clientes_bp.route("/clientes/estadisticas")
@login_requerido
def estadisticas():
    total       = Cliente.query.count()
    por_estado  = db.session.query(Cliente.estado, func.count(Cliente.id)).group_by(Cliente.estado).all()
    por_fuente  = db.session.query(Cliente.fuente,  func.count(Cliente.id)).group_by(Cliente.fuente).all()
    esta_semana = Cliente.query.filter(Cliente.fecha_registro >= datetime.now() - timedelta(days=7)).count()
    este_mes    = Cliente.query.filter(Cliente.fecha_registro >= datetime.now() - timedelta(days=30)).count()
    por_producto = (
        db.session.query(Cliente.producto_interes, func.count(Cliente.id))
        .filter(Cliente.producto_interes != None, Cliente.producto_interes != "")
        .group_by(Cliente.producto_interes)
        .order_by(func.count(Cliente.id).desc())
        .limit(5)
        .all()
    )
    return render_template(
        "admin/clientes/estadisticas.html",
        total=total,
        por_estado=por_estado,
        por_fuente=por_fuente,
        esta_semana=esta_semana,
        este_mes=este_mes,
        por_producto=por_producto,
    )


@clientes_bp.route("/clientes/eliminar/<int:id>", methods=["POST"])
@login_requerido
def eliminar(id):
    cliente = Cliente.query.get_or_404(id)
    nombre = cliente.nombre
    db.session.delete(cliente)
    db.session.commit()
    flash(f"Cliente '{nombre}' eliminado.", "warning")
    return redirect(url_for("clientes.lista"))
