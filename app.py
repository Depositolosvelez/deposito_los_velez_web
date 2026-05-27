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
    # ================= CREAR TABLAS =================
    with app.app_context():
        db.create_all()

        # ================= SEED INVENTARIO =================
        from models import Producto
        if Producto.query.count() < 20:
            DESC = "Consultar precio. Material de segunda en buen estado."
            inventario = [
                # BAÑOS Y SANITARIOS
                ("Sanitario clásico",                    "BAÑOS Y SANITARIOS"),
                ("Sanitario moderno de palanca",          "BAÑOS Y SANITARIOS"),
                ("Sanitario moderno de botón",            "BAÑOS Y SANITARIOS"),
                ("Sanitario Montecarlo",                  "BAÑOS Y SANITARIOS"),
                ("Orinal",                                "BAÑOS Y SANITARIOS"),
                ("Lavamanos cuadrado grande",             "BAÑOS Y SANITARIOS"),
                ("Lavamanos cuadrado pequeño",            "BAÑOS Y SANITARIOS"),
                ("Lavamanos redondo moderno",             "BAÑOS Y SANITARIOS"),
                ("Lavamanos grande",                      "BAÑOS Y SANITARIOS"),
                ("Bañera pequeña",                        "BAÑOS Y SANITARIOS"),
                ("Bañera mediana",                        "BAÑOS Y SANITARIOS"),
                ("Bañera grande",                         "BAÑOS Y SANITARIOS"),
                ("Cabina de baño en acrílico",            "BAÑOS Y SANITARIOS"),
                ("Accesorio baño - toallero",             "BAÑOS Y SANITARIOS"),
                ("Accesorio baño - papelera",             "BAÑOS Y SANITARIOS"),
                ("Accesorio baño - jabonera",             "BAÑOS Y SANITARIOS"),
                # PUERTAS
                ("Puerta de hierro frontal",              "PUERTAS"),
                ("Puerta de hierro patio",                "PUERTAS"),
                ("Puerta entamborada",                    "PUERTAS"),
                ("Puerta madera maciza",                  "PUERTAS"),
                ("Puerta de vidrio",                      "PUERTAS"),
                ("Puerta con malla",                      "PUERTAS"),
                ("Portón",                                "PUERTAS"),
                # REJAS Y VENTANAS
                ("Reja de puerta",                        "REJAS Y VENTANAS"),
                ("Reja de ventana",                       "REJAS Y VENTANAS"),
                ("Ventana",                               "REJAS Y VENTANAS"),
                ("Protector de puerta",                   "REJAS Y VENTANAS"),
                ("Protector de ventana",                  "REJAS Y VENTANAS"),
                # TECHOS Y CUBIERTAS
                ("Teja de zinc",                          "TECHOS Y CUBIERTAS"),
                ("Teja arquitectónica recubierta",        "TECHOS Y CUBIERTAS"),
                ("Teja arquitectónica termoacústica",     "TECHOS Y CUBIERTAS"),
                ("Teja arquitectónica fibra de vidrio",   "TECHOS Y CUBIERTAS"),
                ("Eternit #4",                            "TECHOS Y CUBIERTAS"),
                ("Eternit #6",                            "TECHOS Y CUBIERTAS"),
                ("Teja arquitectónica de lámina",         "TECHOS Y CUBIERTAS"),
                ("Caballete para techo eternit",          "TECHOS Y CUBIERTAS"),
                ("Caballete para techo termoacústico",    "TECHOS Y CUBIERTAS"),
                ("Canaleta de agua",                      "TECHOS Y CUBIERTAS"),
                ("Viga canal de agua",                    "TECHOS Y CUBIERTAS"),
                ("Cercha",                                "TECHOS Y CUBIERTAS"),
                # TUBERÍA PVC
                ('Tubo PVC verde 2"',                     "TUBERÍA PVC"),
                ('Tubo PVC verde 3"',                     "TUBERÍA PVC"),
                ('Tubo PVC verde 4"',                     "TUBERÍA PVC"),
                ('Tubo PVC verde 6"',                     "TUBERÍA PVC"),
                ('Tubo PVC amarillo 2"',                  "TUBERÍA PVC"),
                ('Tubo PVC amarillo 3"',                  "TUBERÍA PVC"),
                ('Tubo PVC amarillo 4"',                  "TUBERÍA PVC"),
                ('Tubo PVC amarillo 6"',                  "TUBERÍA PVC"),
                # ACCESORIOS PVC
                ("Codo PVC",                              "ACCESORIOS PVC"),
                ("YE PVC",                                "ACCESORIOS PVC"),
                ("Semicodo PVC",                          "ACCESORIOS PVC"),
                ("Unión PVC",                             "ACCESORIOS PVC"),
                # TUBERÍA HIERRO GALVANIZADO
                ('Tubo hierro galvanizado 1/2"',          "TUBERÍA HIERRO GALVANIZADO"),
                ('Tubo hierro galvanizado 3/4"',          "TUBERÍA HIERRO GALVANIZADO"),
                ('Tubo hierro galvanizado 1"',            "TUBERÍA HIERRO GALVANIZADO"),
                ('Tubo hierro galvanizado 2"',            "TUBERÍA HIERRO GALVANIZADO"),
                # CABLE ELÉCTRICO
                ("Cable cobre N8",                        "CABLE ELÉCTRICO"),
                ("Cable cobre N10",                       "CABLE ELÉCTRICO"),
                ("Cable cobre N12",                       "CABLE ELÉCTRICO"),
                ("Cable cobre N14",                       "CABLE ELÉCTRICO"),
                ("Cable encauchetado 2x10",               "CABLE ELÉCTRICO"),
                ("Cable encauchetado 2x12",               "CABLE ELÉCTRICO"),
                ("Cable encauchetado 3x10",               "CABLE ELÉCTRICO"),
                ("Cable encauchetado 3x12",               "CABLE ELÉCTRICO"),
                ("Cable encauchetado 4x12",               "CABLE ELÉCTRICO"),
                # GUAYA Y GUAYUA
                ("Guayua eléctrica aluminio N2",          "GUAYA Y GUAYUA"),
                ("Guayua eléctrica aluminio N4",          "GUAYA Y GUAYUA"),
                ("Trenza aluminio N2",                    "GUAYA Y GUAYUA"),
                ("Trenza aluminio N4",                    "GUAYA Y GUAYUA"),
                ('Guaya acerada alma acero 1/4"',         "GUAYA Y GUAYUA"),
                ('Guaya alma yute 1/8"',                  "GUAYA Y GUAYUA"),
                ('Guaya alma yute 3/8"',                  "GUAYA Y GUAYUA"),
                ('Guaya alma yute 5/8"',                  "GUAYA Y GUAYUA"),
                # SEGURIDAD INDUSTRIAL
                ("Arnés de altura",                       "SEGURIDAD INDUSTRIAL"),
                ("Arnés dieléctrico",                     "SEGURIDAD INDUSTRIAL"),
                ("Eslinga",                               "SEGURIDAD INDUSTRIAL"),
                ("Pretales",                              "SEGURIDAD INDUSTRIAL"),
                ("Tay off",                               "SEGURIDAD INDUSTRIAL"),
                ("Casco de seguridad",                    "SEGURIDAD INDUSTRIAL"),
                ("Línea de vida",                         "SEGURIDAD INDUSTRIAL"),
                ("Cono de seguridad vial",                "SEGURIDAD INDUSTRIAL"),
                ("Paleta pare y siga",                    "SEGURIDAD INDUSTRIAL"),
                # HERRAMIENTA Y FERRETERÍA
                ("Pico",                                  "HERRAMIENTA Y FERRETERÍA"),
                ("Pala",                                  "HERRAMIENTA Y FERRETERÍA"),
                ("Palacoca",                              "HERRAMIENTA Y FERRETERÍA"),
                ("Barra",                                 "HERRAMIENTA Y FERRETERÍA"),
                ("Buggy/Carreta de construcción",         "HERRAMIENTA Y FERRETERÍA"),
                ('Doblatubos 1/2"',                       "HERRAMIENTA Y FERRETERÍA"),
                ('Doblatubos 3/4"',                       "HERRAMIENTA Y FERRETERÍA"),
                ("Polea",                                  "HERRAMIENTA Y FERRETERÍA"),
                ("Varilla de segunda",                    "HERRAMIENTA Y FERRETERÍA"),
                ("Escalera de caracol",                   "HERRAMIENTA Y FERRETERÍA"),
                ("Escalera recta segundo piso",           "HERRAMIENTA Y FERRETERÍA"),
                ("Escalera de aluminio",                  "HERRAMIENTA Y FERRETERÍA"),
                # MAQUINARIA Y EQUIPOS
                ("Motor puerta eléctrica",                "MAQUINARIA Y EQUIPOS"),
                ("Planta eléctrica",                      "MAQUINARIA Y EQUIPOS"),
                ("Motobomba",                             "MAQUINARIA Y EQUIPOS"),
                ("Electrobomba pequeña",                  "MAQUINARIA Y EQUIPOS"),
                ("Electrobomba mediana",                  "MAQUINARIA Y EQUIPOS"),
                ("Electrobomba grande",                   "MAQUINARIA Y EQUIPOS"),
                ("Transformador 5KVA",                    "MAQUINARIA Y EQUIPOS"),
                ("Transformador 10KVA",                   "MAQUINARIA Y EQUIPOS"),
                ("Transformador 15KVA",                   "MAQUINARIA Y EQUIPOS"),
                ("Transformador 25KVA",                   "MAQUINARIA Y EQUIPOS"),
                # COCINA
                ("Mueble de cocina guardar platos",       "COCINA"),
                ("Horno de empotrar",                     "COCINA"),
                ("Horno pizzero",                         "COCINA"),
                ("Asador de pollos",                      "COCINA"),
                ("Estufa de empotrar",                    "COCINA"),
                ("Estufa mesa 2 puestos",                 "COCINA"),
                ("Estufa mesa 4 puestos",                 "COCINA"),
                ("Mesón 1m",                              "COCINA"),
                ("Mesón otras medidas",                   "COCINA"),
                ("Mesón en L",                            "COCINA"),
                ("Mesón con estufa empotrada",            "COCINA"),
                ("Mesón con estufa integrada",            "COCINA"),
                ("Lavaplatos sencillo",                   "COCINA"),
                ("Lavaplatos doble",                      "COCINA"),
                # MALLAS
                ("Malla gallinero",                       "MALLAS"),
                ("Malla galvanizada cerramiento",         "MALLAS"),
                # HERRAJE ELÉCTRICO
                ("Breakers de luz",                       "HERRAJE ELÉCTRICO"),
                # VARIOS
                ("Vitrina",                               "VARIOS"),
                ("Estantería",                            "VARIOS"),
                ("Silla sala de espera",                  "VARIOS"),
                ("Canasta plástica",                      "VARIOS"),
                ("Caneca 55 galones",                     "VARIOS"),
                ("Balde",                                 "VARIOS"),
                ("Estera puerta negocio",                 "VARIOS"),
                ("Mesa/barra en acero",                   "VARIOS"),
                ("Barra en acero",                        "VARIOS"),
            ]
            for nombre, categoria in inventario:
                db.session.add(Producto(nombre=nombre, precio=0, categoria=categoria, descripcion=DESC))
            db.session.commit()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config["DEBUG"])
