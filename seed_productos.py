"""
Script para insertar productos masivamente en la base de datos de Vélez Depósitos.
Ejecutar desde la raíz del proyecto: python seed_productos.py
"""
import sqlite3
import os
 
productos = [
    # BAÑOS Y SANITARIOS
    ("Sanitario clásico", 0, "BAÑOS Y SANITARIOS", "Sanitario de segunda, listo para instalar. Consultar precio."),
    ("Sanitario moderno de palanca", 0, "BAÑOS Y SANITARIOS", "Sanitario de segunda, listo para instalar. Consultar precio."),
    ("Sanitario moderno de botón", 0, "BAÑOS Y SANITARIOS", "Sanitario de segunda, listo para instalar. Consultar precio."),
    ("Sanitario Montecarlo", 0, "BAÑOS Y SANITARIOS", "Sanitario de segunda, listo para instalar. Consultar precio."),
    ("Orinal", 0, "BAÑOS Y SANITARIOS", "Orinal de segunda en buen estado. Consultar precio."),
    ("Lavamanos cuadrado grande", 0, "BAÑOS Y SANITARIOS", "Lavamanos de segunda en buen estado. Consultar precio."),
    ("Lavamanos cuadrado pequeño", 0, "BAÑOS Y SANITARIOS", "Lavamanos de segunda en buen estado. Consultar precio."),
    ("Lavamanos redondo moderno", 0, "BAÑOS Y SANITARIOS", "Lavamanos de segunda en buen estado. Consultar precio."),
    ("Lavamanos grande", 0, "BAÑOS Y SANITARIOS", "Lavamanos de segunda en buen estado. Consultar precio."),
    ("Bañera pequeña", 0, "BAÑOS Y SANITARIOS", "Bañera de segunda en buen estado. Consultar precio."),
    ("Bañera mediana", 0, "BAÑOS Y SANITARIOS", "Bañera de segunda en buen estado. Consultar precio."),
    ("Bañera grande", 0, "BAÑOS Y SANITARIOS", "Bañera de segunda en buen estado. Consultar precio."),
    ("Cabina de baño en acrílico", 0, "BAÑOS Y SANITARIOS", "Cabina de baño de segunda en buen estado. Consultar precio."),
    ("Accesorio baño - toallero", 0, "BAÑOS Y SANITARIOS", "Toallero de segunda en buen estado. Consultar precio."),
    ("Accesorio baño - papelera", 0, "BAÑOS Y SANITARIOS", "Papelera de segunda en buen estado. Consultar precio."),
    ("Accesorio baño - jabonera", 0, "BAÑOS Y SANITARIOS", "Jabonera de segunda en buen estado. Consultar precio."),
    # PUERTAS
    ("Puerta de hierro frontal", 0, "PUERTAS", "Puerta de hierro de segunda, resistente y lista para instalar. Consultar precio."),
    ("Puerta de hierro patio", 0, "PUERTAS", "Puerta de hierro de segunda, resistente y lista para instalar. Consultar precio."),
    ("Puerta entamborada", 0, "PUERTAS", "Puerta entamborada de segunda en buen estado. Consultar precio."),
    ("Puerta madera maciza", 0, "PUERTAS", "Puerta de madera maciza de segunda. Consultar precio."),
    ("Puerta de vidrio", 0, "PUERTAS", "Puerta de vidrio de segunda en buen estado. Consultar precio."),
    ("Puerta con malla", 0, "PUERTAS", "Puerta con malla de segunda en buen estado. Consultar precio."),
    ("Portón", 0, "PUERTAS", "Portón de segunda, resistente. Consultar precio."),
    # REJAS Y VENTANAS
    ("Reja de puerta", 0, "REJAS Y VENTANAS", "Reja de segunda en buen estado. Consultar precio."),
    ("Reja de ventana", 0, "REJAS Y VENTANAS", "Reja de segunda en buen estado. Consultar precio."),
    ("Ventana", 0, "REJAS Y VENTANAS", "Ventana de segunda en buen estado. Consultar precio."),
    ("Protector de puerta", 0, "REJAS Y VENTANAS", "Protector de puerta de segunda. Consultar precio."),
    ("Protector de ventana", 0, "REJAS Y VENTANAS", "Protector de ventana de segunda. Consultar precio."),
    # TECHOS Y CUBIERTAS
    ("Teja de zinc", 0, "TECHOS Y CUBIERTAS", "Teja de zinc de segunda en buen estado. Consultar precio."),
    ("Teja arquitectónica recubierta", 0, "TECHOS Y CUBIERTAS", "Teja arquitectónica de segunda. Consultar precio."),
    ("Teja arquitectónica termoacústica", 0, "TECHOS Y CUBIERTAS", "Teja termoacústica de segunda. Consultar precio."),
    ("Teja arquitectónica fibra de vidrio", 0, "TECHOS Y CUBIERTAS", "Teja de fibra de vidrio de segunda. Consultar precio."),
    ("Eternit #4", 0, "TECHOS Y CUBIERTAS", "Eternit #4 de segunda en buen estado. Consultar precio."),
    ("Eternit #6", 0, "TECHOS Y CUBIERTAS", "Eternit #6 de segunda en buen estado. Consultar precio."),
    ("Teja arquitectónica de lámina", 0, "TECHOS Y CUBIERTAS", "Teja de lámina de segunda. Consultar precio."),
    ("Caballete para techo eternit", 0, "TECHOS Y CUBIERTAS", "Caballete de segunda en buen estado. Consultar precio."),
    ("Caballete para techo termoacústico", 0, "TECHOS Y CUBIERTAS", "Caballete de segunda en buen estado. Consultar precio."),
    ("Canaleta de agua", 0, "TECHOS Y CUBIERTAS", "Canaleta de agua de segunda. Consultar precio."),
    ("Viga canal de agua", 0, "TECHOS Y CUBIERTAS", "Viga canal de segunda. Consultar precio."),
    ("Cercha", 0, "TECHOS Y CUBIERTAS", "Cercha de segunda en buen estado. Consultar precio."),
    # TUBERÍA PVC
    ('Tubo PVC verde 2"', 0, "TUBERÍA PVC", "Tubo PVC verde de segunda. Consultar precio."),
    ('Tubo PVC verde 3"', 0, "TUBERÍA PVC", "Tubo PVC verde de segunda. Consultar precio."),
    ('Tubo PVC verde 4"', 0, "TUBERÍA PVC", "Tubo PVC verde de segunda. Consultar precio."),
    ('Tubo PVC verde 6"', 0, "TUBERÍA PVC", "Tubo PVC verde de segunda. Consultar precio."),
    ('Tubo PVC amarillo 2"', 0, "TUBERÍA PVC", "Tubo PVC amarillo de segunda. Consultar precio."),
    ('Tubo PVC amarillo 3"', 0, "TUBERÍA PVC", "Tubo PVC amarillo de segunda. Consultar precio."),
    ('Tubo PVC amarillo 4"', 0, "TUBERÍA PVC", "Tubo PVC amarillo de segunda. Consultar precio."),
    ('Tubo PVC amarillo 6"', 0, "TUBERÍA PVC", "Tubo PVC amarillo de segunda. Consultar precio."),
    # ACCESORIOS PVC
    ("Codo PVC", 0, "ACCESORIOS PVC", "Codo PVC de segunda. Consultar precio."),
    ("YE PVC", 0, "ACCESORIOS PVC", "YE PVC de segunda. Consultar precio."),
    ("Semicodo PVC", 0, "ACCESORIOS PVC", "Semicodo PVC de segunda. Consultar precio."),
    ("Unión PVC", 0, "ACCESORIOS PVC", "Unión PVC de segunda. Consultar precio."),
    # TUBERÍA HIERRO GALVANIZADO
    ('Tubo hierro galvanizado 1/2"', 0, "TUBERÍA HIERRO GALVANIZADO", "Tubo de hierro galvanizado de segunda. Consultar precio."),
    ('Tubo hierro galvanizado 3/4"', 0, "TUBERÍA HIERRO GALVANIZADO", "Tubo de hierro galvanizado de segunda. Consultar precio."),
    ('Tubo hierro galvanizado 1"', 0, "TUBERÍA HIERRO GALVANIZADO", "Tubo de hierro galvanizado de segunda. Consultar precio."),
    ('Tubo hierro galvanizado 2"', 0, "TUBERÍA HIERRO GALVANIZADO", "Tubo de hierro galvanizado de segunda. Consultar precio."),
    # CABLE ELÉCTRICO
    ("Cable cobre N8", 0, "CABLE ELÉCTRICO", "Cable de cobre de segunda. Consultar precio."),
    ("Cable cobre N10", 0, "CABLE ELÉCTRICO", "Cable de cobre de segunda. Consultar precio."),
    ("Cable cobre N12", 0, "CABLE ELÉCTRICO", "Cable de cobre de segunda. Consultar precio."),
    ("Cable cobre N14", 0, "CABLE ELÉCTRICO", "Cable de cobre de segunda. Consultar precio."),
    ("Cable encauchetado 2x10", 0, "CABLE ELÉCTRICO", "Cable encauchetado de segunda. Consultar precio."),
    ("Cable encauchetado 2x12", 0, "CABLE ELÉCTRICO", "Cable encauchetado de segunda. Consultar precio."),
    ("Cable encauchetado 3x10", 0, "CABLE ELÉCTRICO", "Cable encauchetado de segunda. Consultar precio."),
    ("Cable encauchetado 3x12", 0, "CABLE ELÉCTRICO", "Cable encauchetado de segunda. Consultar precio."),
    ("Cable encauchetado 4x12", 0, "CABLE ELÉCTRICO", "Cable encauchetado de segunda. Consultar precio."),
    # GUAYA Y GUAYUA
    ("Guayua eléctrica aluminio N2", 0, "GUAYA Y GUAYUA", "Guayua eléctrica de segunda. Consultar precio."),
    ("Guayua eléctrica aluminio N4", 0, "GUAYA Y GUAYUA", "Guayua eléctrica de segunda. Consultar precio."),
    ("Trenza aluminio N2", 0, "GUAYA Y GUAYUA", "Trenza de aluminio de segunda. Consultar precio."),
    ("Trenza aluminio N4", 0, "GUAYA Y GUAYUA", "Trenza de aluminio de segunda. Consultar precio."),
    ('Guaya acerada alma acero 1/4"', 0, "GUAYA Y GUAYUA", "Guaya acerada de segunda. Consultar precio."),
    ('Guaya alma yute 1/8"', 0, "GUAYA Y GUAYUA", "Guaya alma yute de segunda. Consultar precio."),
    ('Guaya alma yute 3/8"', 0, "GUAYA Y GUAYUA", "Guaya alma yute de segunda. Consultar precio."),
    ('Guaya alma yute 5/8"', 0, "GUAYA Y GUAYUA", "Guaya alma yute de segunda. Consultar precio."),
    # SEGURIDAD INDUSTRIAL
    ("Arnés de altura", 0, "SEGURIDAD INDUSTRIAL", "Arnés de segunda en buen estado. Consultar precio."),
    ("Arnés dieléctrico", 0, "SEGURIDAD INDUSTRIAL", "Arnés dieléctrico de segunda. Consultar precio."),
    ("Eslinga", 0, "SEGURIDAD INDUSTRIAL", "Eslinga de segunda en buen estado. Consultar precio."),
    ("Pretales", 0, "SEGURIDAD INDUSTRIAL", "Pretales de segunda. Consultar precio."),
    ("Tay off", 0, "SEGURIDAD INDUSTRIAL", "Tay off de segunda. Consultar precio."),
    ("Casco de seguridad", 0, "SEGURIDAD INDUSTRIAL", "Casco de seguridad de segunda. Consultar precio."),
    ("Línea de vida", 0, "SEGURIDAD INDUSTRIAL", "Línea de vida de segunda. Consultar precio."),
    ("Cono de seguridad vial", 0, "SEGURIDAD INDUSTRIAL", "Cono de seguridad de segunda. Consultar precio."),
    ("Paleta pare y siga", 0, "SEGURIDAD INDUSTRIAL", "Paleta pare y siga de segunda. Consultar precio."),
    # HERRAMIENTA Y FERRETERÍA
    ("Pico", 0, "HERRAMIENTA Y FERRETERÍA", "Pico de segunda en buen estado. Consultar precio."),
    ("Pala", 0, "HERRAMIENTA Y FERRETERÍA", "Pala de segunda en buen estado. Consultar precio."),
    ("Palacoca", 0, "HERRAMIENTA Y FERRETERÍA", "Palacoca de segunda. Consultar precio."),
    ("Barra", 0, "HERRAMIENTA Y FERRETERÍA", "Barra de segunda en buen estado. Consultar precio."),
    ("Buggy/Carreta de construcción", 0, "HERRAMIENTA Y FERRETERÍA", "Carreta de construcción de segunda. Consultar precio."),
    ('Doblatubos 1/2"', 0, "HERRAMIENTA Y FERRETERÍA", "Doblatubos de segunda. Consultar precio."),
    ('Doblatubos 3/4"', 0, "HERRAMIENTA Y FERRETERÍA", "Doblatubos de segunda. Consultar precio."),
    ("Polea", 0, "HERRAMIENTA Y FERRETERÍA", "Polea de segunda en buen estado. Consultar precio."),
    ("Varilla de segunda", 0, "HERRAMIENTA Y FERRETERÍA", "Varilla de segunda. Consultar precio."),
    ("Escalera de caracol", 0, "HERRAMIENTA Y FERRETERÍA", "Escalera de caracol de segunda. Consultar precio."),
    ("Escalera recta segundo piso", 0, "HERRAMIENTA Y FERRETERÍA", "Escalera recta de segunda. Consultar precio."),
    ("Escalera de aluminio", 0, "HERRAMIENTA Y FERRETERÍA", "Escalera de aluminio de segunda. Consultar precio."),
    # MAQUINARIA Y EQUIPOS
    ("Motor puerta eléctrica", 0, "MAQUINARIA Y EQUIPOS", "Motor para puerta eléctrica de segunda. Consultar precio."),
    ("Planta eléctrica", 0, "MAQUINARIA Y EQUIPOS", "Planta eléctrica de segunda. Consultar precio."),
    ("Motobomba", 0, "MAQUINARIA Y EQUIPOS", "Motobomba de segunda en buen estado. Consultar precio."),
    ("Electrobomba pequeña", 0, "MAQUINARIA Y EQUIPOS", "Electrobomba de segunda. Consultar precio."),
    ("Electrobomba mediana", 0, "MAQUINARIA Y EQUIPOS", "Electrobomba de segunda. Consultar precio."),
    ("Electrobomba grande", 0, "MAQUINARIA Y EQUIPOS", "Electrobomba de segunda. Consultar precio."),
    ("Transformador 5KVA", 0, "MAQUINARIA Y EQUIPOS", "Transformador de segunda. Consultar precio."),
    ("Transformador 10KVA", 0, "MAQUINARIA Y EQUIPOS", "Transformador de segunda. Consultar precio."),
    ("Transformador 15KVA", 0, "MAQUINARIA Y EQUIPOS", "Transformador de segunda. Consultar precio."),
    ("Transformador 25KVA", 0, "MAQUINARIA Y EQUIPOS", "Transformador de segunda. Consultar precio."),
    # COCINA
    ("Mueble de cocina guardar platos", 0, "COCINA", "Mueble de cocina de segunda. Consultar precio."),
    ("Horno de empotrar", 0, "COCINA", "Horno de empotrar de segunda. Consultar precio."),
    ("Horno pizzero", 0, "COCINA", "Horno pizzero de segunda. Consultar precio."),
    ("Asador de pollos", 0, "COCINA", "Asador de pollos de segunda. Consultar precio."),
    ("Estufa de empotrar", 0, "COCINA", "Estufa de empotrar de segunda. Consultar precio."),
    ("Estufa mesa 2 puestos", 0, "COCINA", "Estufa de segunda en buen estado. Consultar precio."),
    ("Estufa mesa 4 puestos", 0, "COCINA", "Estufa de segunda en buen estado. Consultar precio."),
    ("Mesón 1m", 0, "COCINA", "Mesón de cocina de segunda. Consultar precio."),
    ("Mesón otras medidas", 0, "COCINA", "Mesón de cocina de segunda. Consultar precio."),
    ("Mesón en L", 0, "COCINA", "Mesón en L de segunda. Consultar precio."),
    ("Mesón con estufa empotrada", 0, "COCINA", "Mesón con estufa de segunda. Consultar precio."),
    ("Mesón con estufa integrada", 0, "COCINA", "Mesón con estufa de segunda. Consultar precio."),
    ("Lavaplatos sencillo", 0, "COCINA", "Lavaplatos de segunda en buen estado. Consultar precio."),
    ("Lavaplatos doble", 0, "COCINA", "Lavaplatos doble de segunda. Consultar precio."),
    # MALLAS
    ("Malla gallinero", 0, "MALLAS", "Malla gallinero de segunda. Consultar precio."),
    ("Malla galvanizada cerramiento", 0, "MALLAS", "Malla galvanizada de segunda. Consultar precio."),
    # HERRAJE ELÉCTRICO
    ("Breakers de luz", 0, "HERRAJE ELÉCTRICO", "Breakers de segunda en buen estado. Consultar precio."),
    # VARIOS
    ("Vitrina", 0, "VARIOS", "Vitrina de segunda en buen estado. Consultar precio."),
    ("Estantería", 0, "VARIOS", "Estantería de segunda. Consultar precio."),
    ("Silla sala de espera", 0, "VARIOS", "Silla de segunda en buen estado. Consultar precio."),
    ("Canasta plástica", 0, "VARIOS", "Canasta plástica de segunda. Consultar precio."),
    ("Caneca 55 galones", 0, "VARIOS", "Caneca de 55 galones de segunda. Consultar precio."),
    ("Balde", 0, "VARIOS", "Balde de segunda. Consultar precio."),
    ("Estera puerta negocio", 0, "VARIOS", "Estera de segunda. Consultar precio."),
    ("Mesa/barra en acero", 0, "VARIOS", "Mesa en acero de segunda. Consultar precio."),
    ("Barra en acero", 0, "VARIOS", "Barra en acero de segunda. Consultar precio."),
]
 
# Conectar a la base de datos
db_path = "instance/deposito.db"
if not os.path.exists(db_path):
    print(f"❌ No se encontró la base de datos en {db_path}")
    print("Rutas disponibles:")
    for root, dirs, files in os.walk("."):
        for f in files:
            if f.endswith(".db"):
                print(f"  {os.path.join(root, f)}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    insertados = 0
    duplicados = 0
    for nombre, precio, categoria, descripcion in productos:
        # Verificar si ya existe
        cursor.execute("SELECT id FROM productos WHERE nombre = ?", (nombre,))
        if cursor.fetchone():
            duplicados += 1
            continue
        cursor.execute(
            "INSERT INTO productos (nombre, precio, categoria, descripcion, foto) VALUES (?, ?, ?, ?, ?)",
            (nombre, precio, categoria, descripcion, None)
        )
        insertados += 1
    
    conn.commit()
    conn.close()
    print(f"✅ Insertados: {insertados} productos")
    print(f"⏭️  Duplicados omitidos: {duplicados}")
    print(f"📦 Total en lista: {len(productos)}")
