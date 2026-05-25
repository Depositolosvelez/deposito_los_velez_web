from datetime import datetime
from extensions import db


class Producto(db.Model):
    __tablename__ = "productos"

    id          = db.Column(db.Integer, primary_key=True)
    nombre      = db.Column(db.String(120), nullable=False)
    precio      = db.Column(db.Float, nullable=False)
    categoria   = db.Column(db.String(80), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    foto        = db.Column(db.String(200), nullable=True)  # nombre del archivo

    def __repr__(self):
        return f"<Producto {self.nombre}>"


class Cliente(db.Model):
    __tablename__ = "clientes"

    id               = db.Column(db.Integer, primary_key=True)
    nombre           = db.Column(db.String(100), nullable=False)
    telefono         = db.Column(db.String(20), nullable=True)
    ciudad           = db.Column(db.String(100), nullable=True)
    producto_interes = db.Column(db.String(200), nullable=True)
    estado           = db.Column(db.String(50), nullable=False, default="Interesado")
    notas            = db.Column(db.Text, nullable=True)
    fecha_registro   = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Cliente {self.nombre}>"
