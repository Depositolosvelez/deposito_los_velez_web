import re
import unicodedata
from datetime import datetime
from extensions import db


def slugify(texto):
    """Genera slug URL-safe desde texto en español."""
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^\w\s-]', '', texto)
    texto = re.sub(r'[\s_]+', '-', texto)
    texto = re.sub(r'-+', '-', texto)
    return texto.strip('-')


class Producto(db.Model):
    __tablename__ = "productos"
    __table_args__ = (
        db.Index('ix_productos_categoria', 'categoria'),
        db.Index('ix_productos_nombre', 'nombre'),
    )

    UNIDADES_MEDIDA = {
        "UNIDAD":          "Por unidad",
        "METRO":           "Por metro lineal",
        "M2":              "Por m² (ancho x alto)",
        "UNIDAD_VARIABLE": "Por unidad — precio variable (rango)",
    }

    id            = db.Column(db.Integer, primary_key=True)
    nombre        = db.Column(db.String(120), nullable=False)
    precio        = db.Column(db.Float, nullable=False)
    categoria     = db.Column(db.String(80), nullable=False)
    descripcion   = db.Column(db.Text, nullable=True)
    foto          = db.Column(db.String(200), nullable=True)  # nombre del archivo
    unidad_medida = db.Column(db.String(20), nullable=False, default="UNIDAD")  # UNIDAD | METRO | M2 | UNIDAD_VARIABLE
    precio_min    = db.Column(db.Integer, nullable=True)  # solo aplica a UNIDAD_VARIABLE
    precio_max    = db.Column(db.Integer, nullable=True)  # solo aplica a UNIDAD_VARIABLE

    @property
    def slug(self):
        return slugify(self.nombre)

    def __repr__(self):
        return f"<Producto {self.nombre}>"

    @staticmethod
    def _fmt(numero):
        return "${:,.0f}".format(numero).replace(",", ".")

    def precio_principal(self):
        """Monto destacado a mostrar, según la unidad de medida del producto."""
        if self.unidad_medida == "UNIDAD_VARIABLE" and self.precio_min and self.precio_max:
            return f"{self._fmt(self.precio_min)} - {self._fmt(self.precio_max)}"
        if self.unidad_medida == "M2":
            return f"Desde {self._fmt(self.precio)}"
        return self._fmt(self.precio)

    def precio_sufijo(self, largo=True):
        """Texto secundario (unidad de medida / condición) que acompaña al monto."""
        if self.unidad_medida == "METRO":
            return "COP / metro"
        if self.unidad_medida == "M2":
            return "COP (según medida) — cotiza aquí" if largo else "COP (según medida)"
        if self.unidad_medida == "UNIDAD_VARIABLE":
            if self.precio_min and self.precio_max:
                return "COP (según medida y grosor)" if largo else "COP"
            return "COP (según medida)" if largo else "COP"
        return "COP"


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
