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
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config["DEBUG"])
