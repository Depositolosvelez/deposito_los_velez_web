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
