import re
import unicodedata
from datetime import datetime
from extensions import db


def slugify(text):
    """Genera slug URL-safe desde texto en español."""
    text = text.lower().strip()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


class Producto(db.Model):
    __tablename__ = "productos"
    __table_args__ = (
        db.Index('ix_productos_categoria', 'categoria'),
        db.Index('ix_productos_nombre', 'nombre'),
    )

    id          = db.Column(db.Integer, primary_key=True)
    nombre      = db.Column(db.String(120), nullable=False)
    precio      = db.Column(db.Float, nullable=False)
    categoria   = db.Column(db.String(80), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    foto        = db.Column(db.String(200), nullable=True)

    @property
    def slug(self):
        return slugify(self.nombre)

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
    fuente           = db.Column(db.String(50), nullable=True, default="Directo")
    notas            = db.Column(db.Text, nullable=True)
    fecha_registro   = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Cliente {self.nombre}>"
