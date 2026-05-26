import os
from flask import Flask
from dotenv import load_dotenv
from extensions import db
load_dotenv()

def create_app():
    app = Flask(__name__)
    # ================= CONFIGURACIÓN =================
    app.config["SECRET_KEY"]        = os.environ.get("SECRET_KEY", "cambia-esto-en-produccion")
    app.config["DEBUG"]             = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SQLALCHEMY_DATABASE_URI"]        = os.environ.get("DATABASE_URL", "sqlite:///deposito.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # ================= EXTENSIONES =================
    db.init_app(app)
    # ================= BLUEPRINTS =================
    from routes.publicas  import publicas_bp
    from routes.admin     import admin_bp
    from routes.clientes  import clientes_bp
    from routes.sitemap   import sitemap_bp
    app.register_blueprint(publicas_bp)
    app.register_blueprint(admin_bp,    url_prefix="/admin")
    app.register_blueprint(clientes_bp, url_prefix="/admin")
    app.register_blueprint(sitemap_bp)
    # ================= CABECERAS DE SEGURIDAD =================
    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"]        = "DENY"
        response.headers["X-XSS-Protection"]       = "1; mode=block"
        return response
    # ================= SEED TEMPORAL =================
    @app.route("/seed-productos-velez-2026")
    def seed_productos():
        from models import Producto
        productos = [
            ("Sanitario clásico", 0, "BAÑOS Y SANITARIOS"),
            ("Sanitario moderno de palanca", 0, "BAÑOS Y SANITARIOS"),
            ("Sanitario moderno de botón", 0, "BAÑOS Y SANITARIOS"),
            ("Sanitario Montecarlo", 0, "BAÑOS Y SANITARIOS"),
            ("Orinal", 0, "BAÑOS Y SANITARIOS"),
            ("Lavamanos cuadrado grande", 0, "BAÑOS Y SANITARIOS"),
            ("Lavamanos cuadrado pequeño", 0, "BAÑOS Y SANITARIOS"),
            ("Lavamanos redondo moderno", 0, "BAÑOS Y SANITARIOS"),
            ("Lavamanos grande", 0, "BAÑOS Y SANITARIOS"),
            ("Bañera pequeña", 0, "BAÑOS Y SANITARIOS"),
            ("Bañera mediana", 0, "BAÑOS Y SANITARIOS"),
            ("Bañera grande", 0, "BAÑOS Y SANITARIOS"),
            ("Cabina de baño en acrílico", 0, "BAÑOS Y SANITARIOS"),
            ("Accesorio baño - toallero", 0, "BAÑOS Y SANITARIOS"),
            ("Accesorio baño - papelera", 0, "BAÑOS Y SANITARIOS"),
            ("Accesorio baño - jabonera", 0, "BAÑOS Y SANITARIOS"),
            ("Puerta de hierro frontal", 0, "PUERTAS"),
            ("Puerta de hierro patio", 0, "PUERTAS"),
            ("Puerta entamborada", 0, "PUERTAS"),
            ("Puerta madera maciza", 0, "PUERTAS"),
            ("Puerta de vidrio", 0, "PUERTAS"),
            ("Puerta con malla", 0, "PUERTAS"),
            ("Portón", 0, "PUERTAS"),
            ("Reja de puerta", 0, "REJAS Y VENTANAS"),
            ("Reja de ventana", 0, "REJAS Y VENTANAS"),
            ("Ventana", 0, "REJAS Y VENTANAS"),
            ("Protector de puerta", 0, "REJAS Y VENTANAS"),
            ("Protector de ventana", 0, "REJAS Y VENTANAS"),
            ("Teja de zinc", 0, "TECHOS Y CUBIERTAS"),
            ("Teja arquitectónica recubierta", 0, "TECHOS Y CUBIERTAS"),
            ("Teja arquitectónica termoacústica", 0, "TECHOS Y CUBIERTAS"),
            ("Teja arquitectónica fibra de vidrio", 0, "TECHOS Y CUBIERTAS"),
            ("Eternit #4", 0, "TECHOS Y CUBIERTAS"),
            ("Eternit #6", 0, "TECHOS Y CUBIERTAS"),
            ("Teja arquitectónica de lámina", 0, "TECHOS Y CUBIERTAS"),
            ("Caballete para techo eternit", 0, "TECHOS Y CUBIERTAS"),
            ("Caballete para techo termoacústico", 0, "TECHOS Y CUBIERTAS"),
            ("Canaleta de agua", 0, "TECHOS Y CUBIERTAS"),
            ("Viga canal de agua", 0, "TECHOS Y CUBIERTAS"),
            ("Cercha", 0, "TECHOS Y CUBIERTAS"),
            ('Tubo PVC verde 2"', 0, "TUBERÍA PVC"),
            ('Tubo PVC verde 3"', 0, "TUBERÍA PVC"),
            ('Tubo PVC verde 4"', 0, "TUBERÍA PVC"),
            ('Tubo PVC verde 6"', 0, "TUBERÍA PVC"),
            ('Tubo PVC amarillo 2"', 0, "TUBERÍA PVC"),
            ('Tubo PVC amarillo 3"', 0, "TUBERÍA PVC"),
            ('Tubo PVC amarillo 4"', 0, "TUBERÍA PVC"),
            ('Tubo PVC amarillo 6"', 0, "TUBERÍA PVC"),
            ("Codo PVC", 0, "ACCESORIOS PVC"),
            ("YE PVC", 0, "ACCESORIOS PVC"),
            ("Semicodo PVC", 0, "ACCESORIOS PVC"),
            ("Unión PVC", 0, "ACCESORIOS PVC"),
            ('Tubo hierro galvanizado 1/2"', 0, "TUBERÍA HIERRO GALVANIZADO"),
            ('Tubo hierro galvanizado 3/4"', 0, "TUBERÍA HIERRO GALVANIZADO"),
            ('Tubo hierro galvanizado 1"', 0, "TUBERÍA HIERRO GALVANIZADO"),
            ('Tubo hierro galvanizado 2"', 0, "TUBERÍA HIERRO GALVANIZADO"),
            ("Cable cobre N8", 0, "CABLE ELÉCTRICO"),
            ("Cable cobre N10", 0, "CABLE ELÉCTRICO"),
            ("Cable cobre N12", 0, "CABLE ELÉCTRICO"),
            ("Cable cobre N14", 0, "CABLE ELÉCTRICO"),
            ("Cable encauchetado 2x10", 0, "CABLE ELÉCTRICO"),
            ("Cable encauchetado 2x12", 0, "CABLE ELÉCTRICO"),
            ("Cable encauchetado 3x10", 0, "CABLE ELÉCTRICO"),
            ("Cable encauchetado 3x12", 0, "CABLE ELÉCTRICO"),
            ("Cable encauchetado 4x12", 0, "CABLE ELÉCTRICO"),
            ("Guayua eléctrica aluminio N2", 0, "GUAYA Y GUAYUA"),
            ("Guayua eléctrica aluminio N4", 0, "GUAYA Y GUAYUA"),
            ("Trenza aluminio N2", 0, "GUAYA Y GUAYUA"),
            ("Trenza aluminio N4", 0, "GUAYA Y GUAYUA"),
            ('Guaya acerada alma acero 1/4"', 0, "GUAYA Y GUAYUA"),
            ('Guaya alma yute 1/8"', 0, "GUAYA Y GUAYUA"),
            ('Guaya alma yute 3/8"', 0, "GUAYA Y GUAYUA"),
            ('Guaya alma yute 5/8"', 0, "GUAYA Y GUAYUA"),
            ("Arnés de altura", 0, "SEGURIDAD INDUSTRIAL"),
            ("Arnés dieléctrico", 0, "SEGURIDAD INDUSTRIAL"),
            ("Eslinga", 0, "SEGURIDAD INDUSTRIAL"),
            ("Pretales", 0, "SEGURIDAD INDUSTRIAL"),
            ("Tay off", 0, "SEGURIDAD INDUSTRIAL"),
            ("Casco de seguridad", 0, "SEGURIDAD INDUSTRIAL"),
            ("Línea de vida", 0, "SEGURIDAD INDUSTRIAL"),
            ("Cono de seguridad vial", 0, "SEGURIDAD INDUSTRIAL"),
            ("Paleta pare y siga", 0, "SEGURIDAD INDUSTRIAL"),
            ("Pico", 0, "HERRAMIENTA Y FERRETERÍA"),
            ("Pala", 0, "HERRAMIENTA Y FERRETERÍA"),
            ("Palacoca", 0, "HERRAMIENTA Y FERRETERÍA"),
            ("Barra", 0, "HERRAMIENTA Y FERRETERÍA"),
            ("Buggy/Carreta de construcción", 0, "HERRAMIENTA Y FERRETERÍA"),
            ('Doblatubos 1/2"', 0, "HERRAMIENTA Y FERRETERÍA"),
            ('Doblatubos 3/4"', 0, "HERRAMIENTA Y FERRETERÍA"),
            ("Polea", 0, "HERRAMIENTA Y FERRETERÍA"),
            ("Varilla de segunda", 0, "HERRAMIENTA Y FERRETERÍA"),
            ("Escalera de caracol", 0, "HERRAMIENTA Y FERRETERÍA"),
            ("Escalera recta segundo piso", 0, "HERRAMIENTA Y FERRETERÍA"),
            ("Escalera de aluminio", 0, "HERRAMIENTA Y FERRETERÍA"),
            ("Motor puerta eléctrica", 0, "MAQUINARIA Y EQUIPOS"),
            ("Planta eléctrica", 0, "MAQUINARIA Y EQUIPOS"),
            ("Motobomba", 0, "MAQUINARIA Y EQUIPOS"),
            ("Electrobomba pequeña", 0, "MAQUINARIA Y EQUIPOS"),
            ("Electrobomba mediana", 0, "MAQUINARIA Y EQUIPOS"),
            ("Electrobomba grande", 0, "MAQUINARIA Y EQUIPOS"),
            ("Transformador 5KVA", 0, "MAQUINARIA Y EQUIPOS"),
            ("Transformador 10KVA", 0, "MAQUINARIA Y EQUIPOS"),
            ("Transformador 15KVA", 0, "MAQUINARIA Y EQUIPOS"),
            ("Transformador 25KVA", 0, "MAQUINARIA Y EQUIPOS"),
            ("Mueble de cocina guardar platos", 0, "COCINA"),
            ("Horno de empotrar", 0, "COCINA"),
            ("Horno pizzero", 0, "COCINA"),
            ("Asador de pollos", 0, "COCINA"),
            ("Estufa de empotrar", 0, "COCINA"),
            ("Estufa mesa 2 puestos", 0, "COCINA"),
            ("Estufa mesa 4 puestos", 0, "COCINA"),
            ("Mesón 1m", 0, "COCINA"),
            ("Mesón otras medidas", 0, "COCINA"),
            ("Mesón en L", 0, "COCINA"),
            ("Mesón con estufa empotrada", 0, "COCINA"),
            ("Mesón con estufa integrada", 0, "COCINA"),
            ("Lavaplatos sencillo", 0, "COCINA"),
            ("Lavaplatos doble", 0, "COCINA"),
            ("Malla gallinero", 0, "MALLAS"),
            ("Malla galvanizada cerramiento", 0, "MALLAS"),
            ("Breakers de luz", 0, "HERRAJE ELÉCTRICO"),
            ("Vitrina", 0, "VARIOS"),
            ("Estantería", 0, "VARIOS"),
            ("Silla sala de espera", 0, "VARIOS"),
            ("Canasta plástica", 0, "VARIOS"),
            ("Caneca 55 galones", 0, "VARIOS"),
            ("Balde", 0, "VARIOS"),
            ("Estera puerta negocio", 0, "VARIOS"),
            ("Mesa/barra en acero", 0, "VARIOS"),
            ("Barra en acero", 0, "VARIOS"),
        ]
        insertados = 0
        duplicados = 0
        for nombre, precio, categoria in productos:
            if not Producto.query.filter_by(nombre=nombre).first():
                p = Producto(nombre=nombre, precio=precio, categoria=categoria, descripcion="Consultar precio. Material de segunda en buen estado.")
                db.session.add(p)
                insertados += 1
            else:
                duplicados += 1
        db.session.commit()
        return f"✅ Insertados: {insertados} | ⏭️ Duplicados omitidos: {duplicados}"
    # ================= CREAR TABLAS =================
    with app.app_context():
        db.create_all()
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config["DEBUG"])
