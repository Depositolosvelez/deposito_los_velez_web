import os
from flask import Flask
from dotenv import load_dotenv
from extensions import db

# Carga .env y también el archivo llamado 'env' (sin punto) que usa este proyecto
load_dotenv()
load_dotenv('env', override=False)


def create_app():
    app = Flask(__name__)
    # ================= CONFIGURACIÓN =================
    is_debug = os.environ.get("DEBUG", os.environ.get("FLASK_DEBUG", "0")) in ("true", "1")

    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        if is_debug:
            secret_key = "dev-only-insecure-key-never-use-in-prod"
            print("ADVERTENCIA: SECRET_KEY no definida. Usando clave de desarrollo insegura.")
        else:
            raise RuntimeError(
                "SECRET_KEY no está definida. Agrega SECRET_KEY=<valor-aleatorio> al archivo env"
            )
    app.config["SECRET_KEY"] = secret_key
    app.config["DEBUG"]                 = is_debug
    app.config["TEMPLATES_AUTO_RELOAD"] = is_debug  # solo recarga templates en desarrollo

    app.config["SQLALCHEMY_DATABASE_URI"]        = os.environ.get("DATABASE_URL", "sqlite:///deposito.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB máximo por archivo
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
        # CSP: permite recursos propios, Bootstrap CDN, Google (Ads/Maps/Fonts), Meta Pixel
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://www.googletagmanager.com https://www.google-analytics.com https://connect.facebook.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://res.cloudinary.com https://www.google.com https://maps.gstatic.com https://www.facebook.com; "
            "frame-src https://www.google.com; "
            "connect-src 'self' https://www.google-analytics.com https://www.googletagmanager.com https://www.facebook.com https://www.google.com;"
        )
        return response
    # ================= CREAR TABLAS =================
    with app.app_context():
        db.create_all()

        # ================= MIGRACIÓN: COLUMNAS DE UNIDAD DE MEDIDA =================
        # Debe correr antes de cualquier consulta ORM sobre Producto: el modelo ya
        # declara unidad_medida/precio_min/precio_max aunque la tabla en producción
        # todavía no las tenga, y eso rompe hasta un simple Producto.query.count().
        from sqlalchemy import text, inspect as sa_inspect
        columnas_productos = [c["name"] for c in sa_inspect(db.engine).get_columns("productos")]
        if "unidad_medida" not in columnas_productos:
            db.session.execute(text("ALTER TABLE productos ADD COLUMN unidad_medida VARCHAR(20) DEFAULT 'UNIDAD'"))
        if "precio_min" not in columnas_productos:
            db.session.execute(text("ALTER TABLE productos ADD COLUMN precio_min INTEGER"))
        if "precio_max" not in columnas_productos:
            db.session.execute(text("ALTER TABLE productos ADD COLUMN precio_max INTEGER"))
        db.session.commit()
        db.session.execute(text("UPDATE productos SET unidad_medida='UNIDAD' WHERE unidad_medida IS NULL"))
        db.session.commit()

        # ================= SEED INVENTARIO =================
        from models import Producto, CATEGORIA_NUEVA
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
                ("Arnés de altura",                       "SEGURIDAD Y ALTURA"),
                ("Arnés dieléctrico",                     "SEGURIDAD Y ALTURA"),
                ("Eslinga",                               "SEGURIDAD Y ALTURA"),
                ("Pretales",                              "SEGURIDAD Y ALTURA"),
                ("Tay off",                               "SEGURIDAD Y ALTURA"),
                ("Casco de seguridad",                    "SEGURIDAD Y ALTURA"),
                ("Línea de vida",                         "SEGURIDAD Y ALTURA"),
                ("Cono de seguridad vial",                "SEGURIDAD Y ALTURA"),
                ("Paleta pare y siga",                    "SEGURIDAD Y ALTURA"),
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
            ("SEGURIDAD Y ALTURA",        "categoria = 'SEGURIDAD INDUSTRIAL'"),
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

        # ================= MIGRACIÓN: CLASIFICACIÓN DE UNIDADES DE MEDIDA =================
        # Unidad de medida por categoría — ver Actualizacion_Unidades_Medida_POS_Web.md, secciones 1 y 4
        CATEGORIA_UNIDAD = {
            "ACCESORIOS PVC":             "UNIDAD",
            "BAÑOS Y SANITARIOS":         "UNIDAD",
            "CABLE ELÉCTRICO":            "METRO",
            "COCINA":                     "UNIDAD",
            "ESCALERAS DE ALUMINIO":      "UNIDAD_VARIABLE",
            "ESCALERAS ESTRUCTURALES":    "UNIDAD_VARIABLE",
            "GUAYAS EN ACERO":            "METRO",
            "GUAYAS EN ALUMINIO":         "METRO",
            "HERRAJE ELÉCTRICO":          "UNIDAD",
            "HERRAMIENTA Y FERRETERÍA":   "UNIDAD",
            "HORNOS":                     "UNIDAD",
            "LAVAPLATOS":                 "UNIDAD",
            "MALLAS":                     "UNIDAD",
            CATEGORIA_NUEVA:              "UNIDAD",
            "MAQUINARIA Y EQUIPOS":       "UNIDAD",
            "PUERTAS":                    "UNIDAD",   # excepción: puertas de hierro (ver abajo)
            "REJAS Y PROTECTORES":        "M2",
            "SEGURIDAD Y ALTURA":         "UNIDAD",
            "TECHOS Y CUBIERTAS":         "UNIDAD",   # excepción: tejas (ver abajo)
            "TRANSFORMADORES":            "UNIDAD",
            "TUBERÍA HIERRO GALVANIZADO": "METRO",
            "TUBERÍA PVC":                "METRO",
            "VARIOS":                     "UNIDAD",
            "VENTANAS":                   "M2",
        }
        for cat_nombre, unidad in CATEGORIA_UNIDAD.items():
            db.session.execute(
                text("UPDATE productos SET unidad_medida=:u WHERE categoria=:c AND unidad_medida='UNIDAD'"),
                {"u": unidad, "c": cat_nombre},
            )

        # Excepciones dentro de categorías mixtas (solo se aplican una vez, mientras sigan en 'UNIDAD')
        db.session.execute(text(
            "UPDATE productos SET unidad_medida='METRO' "
            "WHERE categoria='TECHOS Y CUBIERTAS' AND LOWER(nombre) LIKE 'teja arquitect%' AND unidad_medida='UNIDAD'"
        ))
        db.session.execute(text(
            "UPDATE productos SET unidad_medida='UNIDAD_VARIABLE', precio_min=450000, precio_max=600000 "
            "WHERE categoria='PUERTAS' AND LOWER(nombre) LIKE 'puerta%hierro%' AND unidad_medida='UNIDAD'"
        ))
        db.session.commit()

        # ================= MIGRACIÓN: PRECIOS SINCRONIZADOS CON EL POS (2026-10-15) =================
        # Cada UPDATE exige el valor anterior en el WHERE: se aplica una sola vez y no pisa
        # cambios hechos después desde el panel admin.
        sync_pos = [
            "UPDATE productos SET precio=10000 WHERE id=49 AND precio=4000",   # Codo PVC
            "UPDATE productos SET precio=2500 WHERE id=70 AND precio=25000",   # Guaya acerada 1/4"
            "UPDATE productos SET precio=12000 WHERE id=68 AND precio=10000",  # Trenza aluminio #2 segunda
            "UPDATE productos SET precio=10000 WHERE id=136 AND precio=9000",  # Trenza #4 nueva
            # Eternit se vende por hoja, no por metro
            "UPDATE productos SET precio=15000, unidad_medida='UNIDAD' WHERE id=33 AND precio=25000",
            "UPDATE productos SET precio=25000, unidad_medida='UNIDAD' WHERE id=34 AND precio=60000",
            # Zinc: por hoja, separado en 3 m y 2 m como en el POS
            "UPDATE productos SET nombre='Teja de zinc 3 m', precio=25000, unidad_medida='UNIDAD' "
            "WHERE id=29 AND precio=8000",
            "UPDATE productos SET precio=450000, precio_min=400000 "
            "WHERE id=18 AND unidad_medida='UNIDAD_VARIABLE' AND precio_min=450000",  # Puerta hierro patio
            "UPDATE productos SET precio=250000, precio_min=250000, precio_max=550000 "
            "WHERE id=94 AND precio_min IS NULL",  # Escalera aluminio 3 a 10 pasos
            "UPDATE productos SET unidad_medida='UNIDAD_VARIABLE', precio=120000, precio_min=120000, precio_max=280000 "
            "WHERE id=5 AND unidad_medida='UNIDAD'",  # Orinal pequeño a grande
            # El portón quedó atrapado en el rango de puertas de hierro; su precio real está en la descripción
            "UPDATE productos SET unidad_medida='UNIDAD', precio=2300000, precio_min=NULL, precio_max=NULL "
            "WHERE id=23 AND unidad_medida='UNIDAD_VARIABLE'",
            "UPDATE productos SET precio=100000 WHERE id=76 AND precio=80000",  # Eslinga de posicionamiento
            # La malla eslabonada repetía las mallas nuevas de cercar: les cede su foto y se elimina
            "UPDATE productos SET foto=(SELECT foto FROM productos WHERE nombre='Malla eslabonada nueva galvanizada - rollo 10 m') "
            "WHERE nombre LIKE 'Malla nueva de cercar%' AND foto IS NULL "
            "AND EXISTS (SELECT 1 FROM productos WHERE nombre='Malla eslabonada nueva galvanizada - rollo 10 m')",
            "DELETE FROM productos WHERE nombre='Malla eslabonada nueva galvanizada - rollo 10 m'",
        ]
        for sql in sync_pos:
            db.session.execute(text(sql))
        zinc3 = Producto.query.filter_by(nombre="Teja de zinc 3 m").first()
        if zinc3 and not Producto.query.filter_by(nombre="Teja de zinc 2 m").first():
            db.session.add(Producto(
                nombre="Teja de zinc 2 m", precio=20000, categoria="TECHOS Y CUBIERTAS", unidad_medida="UNIDAD",
                descripcion=zinc3.descripcion, foto=zinc3.foto,
            ))

        # Productos que estaban en el catálogo del POS pero no en la web
        faltantes_pos = [
            # (nombre, precio, categoria, unidad_medida, precio_min, precio_max, descripcion)
            ("Cable de cobre #6", 9000, "CABLE ELÉCTRICO", "METRO", None, None,
             "Cable de cobre calibre #6 para acometidas y circuitos de alta carga. Material de segunda, revisado y en buen estado. Se vende por metro."),
            ("Cable de cobre #16", 1500, "CABLE ELÉCTRICO", "METRO", None, None,
             "Cable de cobre calibre #16 para iluminación y circuitos de baja carga. Material de segunda, revisado y en buen estado. Se vende por metro."),
            ("Trenza de aluminio 1/0 nueva", 20000, "GUAYAS EN ALUMINIO", "METRO", None, None,
             "Trenza de aluminio calibre 1/0 NUEVA, más gruesa que la #2, para acometidas y redes eléctricas de mayor capacidad. Se vende por metro."),
            ("Trenza de aluminio #2 nueva", 15000, "GUAYAS EN ALUMINIO", "METRO", None, None,
             "Trenza de aluminio calibre #2 NUEVA para acometidas y redes eléctricas. Se vende por metro."),
            ("Trenza de aluminio #4 de segunda", 8000, "GUAYAS EN ALUMINIO", "METRO", None, None,
             "Trenza de aluminio calibre #4 para acometidas y redes eléctricas. Material de segunda, revisado y en buen estado. Se vende por metro."),
            ("Canaleta de agua PVC", 25000, "TECHOS Y CUBIERTAS", "METRO", None, None,
             "Canaleta de agua en PVC para recoger el agua lluvia del techo. Material de segunda, revisado y en buen estado. Se vende por metro."),
            ("Teja eternit #8", 35000, "TECHOS Y CUBIERTAS", "UNIDAD", None, None,
             "Teja de fibrocemento (eternit) #8 para techos de casas, ramadas y bodegas. Material de segunda, revisado y en buen estado. Precio por hoja."),
            ("Canasta plástica", 20000, "VARIOS", "UNIDAD", None, None,
             "Canasta plástica resistente para carga, almacenamiento y transporte de materiales. Material de segunda en buen estado."),
        ] + [
            (f"Escalera de aluminio tijera {pasos} pasos", precio, "ESCALERAS DE ALUMINIO", "UNIDAD_VARIABLE", pmin, pmax,
             f"Escalera tijera de aluminio de {pasos} pasos, liviana y resistente para mantenimiento, pintura y obra. Material de segunda, revisado y en buen estado.")
            for pasos, precio, pmin, pmax in [
                (3, 250000, None, None), (4, 300000, None, None), (5, 350000, None, None), (6, 370000, None, None),
                (7, 400000, None, None), (8, 450000, None, None), (9, 500000, None, None), (10, 550000, 500000, 550000),
            ]
        ]
        for nombre, precio, categoria, unidad, pmin, pmax, descripcion in faltantes_pos:
            if not Producto.query.filter_by(nombre=nombre).first():
                db.session.add(Producto(
                    nombre=nombre, precio=precio, categoria=categoria, unidad_medida=unidad,
                    precio_min=pmin, precio_max=pmax, descripcion=descripcion,
                ))
        db.session.commit()

        # ================= MIGRACIÓN: MALLAS NUEVAS DE CERCAR =================
        # La malla galvanizada de cerramiento ya no se vende; la reemplazan rollos de 10 m de malla nueva.
        db.session.execute(text("DELETE FROM productos WHERE categoria='MALLAS' AND LOWER(nombre) LIKE 'malla galvanizada%'"))
        mallas_cercar = [
            ("Malla nueva de cercar 1,50 m - rollo 10 m", 300000, "1,50"),
            ("Malla nueva de cercar 1,80 m - rollo 10 m", 350000, "1,80"),
            ("Malla nueva de cercar 2 m - rollo 10 m",    400000, "2"),
        ]
        for nombre, precio, alto in mallas_cercar:
            if not Producto.query.filter_by(nombre=nombre).first():
                db.session.add(Producto(
                    nombre=nombre, precio=precio, categoria=CATEGORIA_NUEVA, unidad_medida="UNIDAD",
                    descripcion=f"Malla eslabonada NUEVA para cercar de {alto} m de alto. Se vende por rollo de 10 metros.",
                ))
        db.session.commit()

        # ================= MIGRACIÓN: CATEGORÍA MALLA ESLABONADA (NUEVA) =================
        # Las mallas de cerca son producto nuevo; el resto del inventario es de segunda.
        db.session.execute(
            text("UPDATE productos SET categoria=:cat, "
                 "descripcion=REPLACE(descripcion, 'Malla nueva para cercar', 'Malla eslabonada NUEVA para cercar') "
                 "WHERE nombre LIKE 'Malla nueva de cercar%' AND categoria='MALLAS'"),
            {"cat": CATEGORIA_NUEVA},
        )
        db.session.commit()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config["DEBUG"])
