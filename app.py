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
                # REJAS Y PROTECTORES
                ("Reja de puerta",                        "REJAS Y PROTECTORES"),
                ("Reja de ventana",                       "REJAS Y PROTECTORES"),
                ("Protector de puerta",                   "REJAS Y PROTECTORES"),
                ("Protector de ventana",                  "REJAS Y PROTECTORES"),
                # VENTANAS
                ("Ventana",                               "VENTANAS"),
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
                # GUAYAS EN ALUMINIO
                ("Guayua eléctrica aluminio N2",          "GUAYAS EN ALUMINIO"),
                ("Guayua eléctrica aluminio N4",          "GUAYAS EN ALUMINIO"),
                ("Trenza aluminio N2",                    "GUAYAS EN ALUMINIO"),
                ("Trenza aluminio N4",                    "GUAYAS EN ALUMINIO"),
                # GUAYAS EN ACERO
                ('Guaya acerada alma acero 1/4"',         "GUAYAS EN ACERO"),
                ('Guaya alma yute 1/8"',                  "GUAYAS EN ACERO"),
                ('Guaya alma yute 3/8"',                  "GUAYAS EN ACERO"),
                ('Guaya alma yute 5/8"',                  "GUAYAS EN ACERO"),
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
                # ESCALERAS ESTRUCTURALES
                ("Escalera de caracol",                   "ESCALERAS ESTRUCTURALES"),
                ("Escalera recta segundo piso",           "ESCALERAS ESTRUCTURALES"),
                # ESCALERAS DE ALUMINIO
                ("Escalera de aluminio",                  "ESCALERAS DE ALUMINIO"),
                # MAQUINARIA Y EQUIPOS
                ("Motor puerta eléctrica",                "MAQUINARIA Y EQUIPOS"),
                ("Planta eléctrica",                      "MAQUINARIA Y EQUIPOS"),
                ("Motobomba",                             "MAQUINARIA Y EQUIPOS"),
                ("Electrobomba pequeña",                  "MAQUINARIA Y EQUIPOS"),
                ("Electrobomba mediana",                  "MAQUINARIA Y EQUIPOS"),
                ("Electrobomba grande",                   "MAQUINARIA Y EQUIPOS"),
                # TRANSFORMADORES
                ("Transformador 5KVA",                    "TRANSFORMADORES"),
                ("Transformador 10KVA",                   "TRANSFORMADORES"),
                ("Transformador 15KVA",                   "TRANSFORMADORES"),
                ("Transformador 25KVA",                   "TRANSFORMADORES"),
                # COCINA
                ("Mueble de cocina guardar platos",       "COCINA"),
                ("Horno de empotrar",                     "COCINA"),
                ("Estufa de empotrar",                    "COCINA"),
                ("Estufa mesa 2 puestos",                 "COCINA"),
                ("Estufa mesa 4 puestos",                 "COCINA"),
                # HORNOS
                ("Horno pizzero",                         "HORNOS"),
                ("Asador de pollos",                      "HORNOS"),
                # LAVAPLATOS
                ("Lavaplatos sencillo",                   "LAVAPLATOS"),
                ("Lavaplatos doble",                      "LAVAPLATOS"),
                ("Mesón 1m",                              "LAVAPLATOS"),
                ("Mesón otras medidas",                   "LAVAPLATOS"),
                ("Mesón en L",                            "LAVAPLATOS"),
                ("Mesón con estufa empotrada",            "LAVAPLATOS"),
                ("Mesón con estufa integrada",            "LAVAPLATOS"),
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

        # ================= MIGRACIÓN DE CATEGORÍAS =================
        from sqlalchemy import text
        migraciones = [
            ("BAÑOS Y SANITARIOS",       "categoria LIKE 'BAÑO%'"),
            ("PUERTAS",                  "categoria LIKE 'PUERTA%'"),
            ("CABLE ELÉCTRICO",          "categoria = 'CABLES'"),
            ("SEGURIDAD INDUSTRIAL",     "categoria = 'SEGURIDAD Y ALTURA'"),
            ("VENTANAS",                 "nombre = 'Ventana' AND categoria = 'REJAS Y VENTANAS'"),
            ("REJAS Y PROTECTORES",      "nombre IN ('Reja de puerta','Reja de ventana','Protector de puerta','Protector de ventana')"),
            ("GUAYAS EN ALUMINIO",       "nombre IN ('Guayua eléctrica aluminio N2','Guayua eléctrica aluminio N4','Trenza aluminio N2','Trenza aluminio N4')"),
            ("GUAYAS EN ACERO",          "nombre IN ('Guaya acerada alma acero 1/4\"','Guaya alma yute 1/8\"','Guaya alma yute 3/8\"','Guaya alma yute 5/8\"')"),
            ("ESCALERAS DE ALUMINIO",    "nombre = 'Escalera de aluminio'"),
            ("ESCALERAS ESTRUCTURALES",  "nombre IN ('Escalera de caracol','Escalera recta segundo piso')"),
            ("TRANSFORMADORES",          "nombre IN ('Transformador 5KVA','Transformador 10KVA','Transformador 15KVA','Transformador 25KVA')"),
            ("LAVAPLATOS",               "nombre IN ('Lavaplatos sencillo','Lavaplatos doble','Mesón 1m','Mesón otras medidas','Mesón en L','Mesón con estufa empotrada','Mesón con estufa integrada')"),
            ("HORNOS",                   "nombre IN ('Horno pizzero','Asador de pollos')"),
        ]
        for nueva_cat, condicion in migraciones:
            db.session.execute(text(f"UPDATE productos SET categoria=:cat WHERE {condicion}"), {"cat": nueva_cat})
        db.session.commit()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config["DEBUG"])
