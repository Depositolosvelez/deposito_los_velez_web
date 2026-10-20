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


CATEGORIA_NUEVA = "MALLA ESLABONADA (NUEVA)"

# Grupos de categorías: los mismos en el inicio y en los filtros del catálogo.
# (slug, nombre, ícono del sprite, categorías)
GRUPOS_CATEGORIAS = [
    ("banos-y-cocina",  "Baños y cocina",       "droplet-fill",          ["BAÑOS Y SANITARIOS", "LAVAPLATOS", "COCINA", "HORNOS"]),
    ("puertas-y-rejas", "Puertas y rejas",      "door-closed-fill",      ["PUERTAS", "REJAS Y PROTECTORES", "VENTANAS"]),
    ("techos",          "Techos",               "house-fill",            ["TECHOS Y CUBIERTAS"]),
    ("electrico",       "Eléctrico",            "lightning-charge-fill", ["CABLE ELÉCTRICO", "GUAYAS EN ALUMINIO", "GUAYAS EN ACERO", "HERRAJE ELÉCTRICO", "TRANSFORMADORES"]),
    ("tuberia",         "Tubería",              "water",                 ["TUBERÍA PVC", "ACCESORIOS PVC", "TUBERÍA HIERRO GALVANIZADO"]),
    ("herramienta",     "Herramienta y equipos", "tools",                ["HERRAMIENTA Y FERRETERÍA", "ESCALERAS ESTRUCTURALES", "ESCALERAS DE ALUMINIO", "MAQUINARIA Y EQUIPOS"]),
    ("seguridad",       "Seguridad y altura",   "shield-fill-check",     ["SEGURIDAD Y ALTURA"]),
    ("mallas",          "Mallas",               "grid-3x3-gap-fill",     [CATEGORIA_NUEVA, "MALLAS"]),
    ("varios",          "Varios",               "box-seam-fill",         ["VARIOS"]),
]


def grupos_con(categorias):
    """Grupos con solo las categorías que existen; las que no están en ningún grupo van a Varios."""
    agrupadas = {c for *_, cats in GRUPOS_CATEGORIAS for c in cats}
    sueltas = sorted(c for c in categorias if c not in agrupadas)
    grupos = []
    for slug, nombre, icono, cats in GRUPOS_CATEGORIAS:
        presentes = [c for c in cats if c in categorias] + (sueltas if slug == "varios" else [])
        if presentes:
            grupos.append((slug, nombre, icono, presentes))
    return grupos


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

    @property
    def es_nuevo(self):
        nombre = self.nombre.lower()
        return self.categoria == CATEGORIA_NUEVA or " nueva" in nombre or " nuevo" in nombre

    @property
    def descripcion_corta(self):
        """Descripción para meta tags: condición, precio y texto del producto."""
        condicion = "nuevo" if self.es_nuevo else "de segunda"
        precio = "precio a consultar" if not self.precio else f"{self.precio_principal()} {self.precio_sufijo(largo=False)}"
        texto = f"{self.nombre} {condicion} en Montería, {precio}. {self.descripcion or ''}".strip()
        return texto if len(texto) <= 158 else texto[:155].rsplit(" ", 1)[0] + "…"

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
