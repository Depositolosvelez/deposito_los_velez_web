import csv
import io
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response
from extensions import db
from models import Cliente

clientes_bp = Blueprint("clientes", __name__)

ESTADOS = ["Interesado", "Compró", "Seguimiento", "Frío"]


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
            notas=request.form.get("notas", "").strip(),
        )
        db.session.add(cliente)
        db.session.commit()
        flash(f"Cliente '{nombre}' agregado correctamente.", "success")
        return redirect(url_for("clientes.lista"))

    return render_template("admin/clientes/form.html", cliente=None, estados=ESTADOS)


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
        cliente.notas = request.form.get("notas", "").strip()

        db.session.commit()
        flash(f"Cliente '{cliente.nombre}' actualizado.", "success")
        return redirect(url_for("clientes.lista"))

    return render_template("admin/clientes/form.html", cliente=cliente, estados=ESTADOS)


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


@clientes_bp.route("/clientes/eliminar/<int:id>", methods=["POST"])
@login_requerido
def eliminar(id):
    cliente = Cliente.query.get_or_404(id)
    nombre = cliente.nombre
    db.session.delete(cliente)
    db.session.commit()
    flash(f"Cliente '{nombre}' eliminado.", "warning")
    return redirect(url_for("clientes.lista"))
